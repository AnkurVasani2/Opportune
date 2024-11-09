# Import necessary libraries
import google.generativeai as ai  # Make sure this is installed and imported correctly

# Simulated response object for testing (replace with actual API call in production)
class GenerateContentResponse:
    def __init__(self, done, iterator, _result):
        self.done = done
        self.iterator = iterator
        self._result = _result

# Simulating the content structure similar to what your API would return
class Protos:
    class GenerateContentResponse:
        def __init__(self, candidates):
            self.candidates = candidates

# Create a simulated response object
response = GenerateContentResponse(
    done=True,
    iterator=None,
    _result=Protos.GenerateContentResponse({
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "## Resume Evaluation:\n\n**Overall Score:** 65/100\n\n**Strengths:**\n\n* **Strong Skills:**..."
                        }
                    ],
                    "role": "model"
                },
                "finish_reason": "STOP",
                "index": 0,
                "safety_ratings": [
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "probability": "NEGLIGIBLE"
                    }
                ]
            }
        ],
        "usage_metadata": {
            "prompt_token_count": 1751,
            "candidates_token_count": 734,
            "total_token_count": 2485
        }
    }),
)

# Extracting the overall score
content_text = response._result.candidates[0]['content']['parts'][0]['text']
score_start = content_text.find("Overall Score:") + len("Overall Score: ")
score_end = content_text.find("\n", score_start)
overall_score = content_text[score_start:score_end].strip()

print("Overall Score:", overall_score)  # Output: Overall Score: 65/100
