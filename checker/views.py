# plagiarism_backend/checker/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FileUploadSerializer
from .utils import extract_text_from_pdf, extract_text_from_docx, chunk_text, clean_text
from .google_api import search_google
from .similarity import compute_best_similarity
import io

def similarity_to_color(sim):
    # sim is 0..1
    if sim >= 0.6:
        return "red"
    elif sim >= 0.3:
        return "orange"
    else:
        return "green"

class CheckPlagiarismView(APIView):
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        text = serializer.validated_data.get("text")
        file = serializer.validated_data.get("file")

        extracted_text = ""
        if file:
            # determine file type
            f = file
            filename = f.name.lower()
            try:
                if filename.endswith(".pdf"):
                    # pdfplumber needs binary file-like; f is InMemoryUploadedFile providing .file
                    extracted_text = extract_text_from_pdf(f)
                elif filename.endswith(".docx"):
                    extracted_text = extract_text_from_docx(f)
                else:
                    return Response({"error": "Unsupported file type. Use PDF or DOCX."},
                                    status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": f"Failed to extract text: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif text:
            extracted_text = text
        else:
            return Response({"error": "No text or file provided"}, status=status.HTTP_400_BAD_REQUEST)

        extracted_text = clean_text(extracted_text)
        if not extracted_text:
            return Response({"error": "No extractable text found."}, status=status.HTTP_400_BAD_REQUEST)

        # chunk text
        chunks = chunk_text(extracted_text, max_words=160)

        chunk_results = []
        total_weight = 0.0
        weighted_score_sum = 0.0

        for chunk in chunks:
            # query google for top 3 results
            results = search_google(chunk, num=3)
            best_score, best_result = compute_best_similarity(chunk, results)
            color = similarity_to_color(best_score)
            chunk_len = len(chunk.split())
            # accumulate weight by chunk length
            total_weight += chunk_len
            weighted_score_sum += best_score * chunk_len

            chunk_results.append({
                "text": chunk,
                "similarity": round(best_score, 4),
                "color": color,
                "matched_snippet": best_result.get("snippet") if best_result else "",
                "matched_url": best_result.get("link") if best_result else "",
                "matched_title": best_result.get("title") if best_result else ""
            })

        # overall plagiarism percent: weighted average of best_score per chunk (0..1) scaled to 100
        overall_similarity = (weighted_score_sum / total_weight) if total_weight > 0 else 0.0
        plagiarism_percent = round(overall_similarity * 100, 2)

        response = {
            "plagiarism_percent": plagiarism_percent,
            "chunks": chunk_results,
            "num_chunks": len(chunk_results)
        }
        return Response(response, status=status.HTTP_200_OK)
