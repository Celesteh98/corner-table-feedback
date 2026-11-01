import requests
import streamlit as st

#Settings
BUSINESS = "a casual sit-down resturant"
LABELS = ["food", "service", "value", "atmosphere"]
TONES = ["positive", "negative", "mixed"]
GUIDE = """Give the comment one label and one tone.

Labels (pick exactly one):
- food: the taste, temperature, portion size, or quality of the dishes.
- service: how the staff treated the customer, including friendliness, mistakes and how long they waited.
- value: whether the meal felt worth the price.
- atmosphere: clealiness, noise, seating or the overall feel of the space.
If the comment covers more than one, pick the one it complains about most.

Tone (pick exactly one): positive, negative, or mixed. Sarcasm counts as negative.

Answer with only the label and the tone, seperated by a comma. For example: food, positive"""

URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-20b"   # check Groq's current free models here: https://console.groq.com/docs/rate-limits$0

def label_comment(text):
  key = st.secrets["GROQ_API_KEY"]
  prompt = f"You label customer comments for {BUSINESS}. \n{GUIDE}\n\nComment: {text}"
  response = requests.post(
      URL,
      headers={"Authorization": f"Bearer {key}"},
      json={
          "model": MODEL,
          "temperature": 0,
          "messages": [{
              "role": "user", "content": prompt}]},
      timeout=30,
    )
  response.raise_for_status()
  answer = response.json()["choices"][0]["message"]["content"]
  return read_answer(answer)

def read_answer(answer):
  parts = [p.strip(" .\n").lower() for p in answer.split(",")]
  label = parts[0] if parts and parts[0] in LABELS else "unclear"
  tone = parts[1] if len(parts)>1 and parts[1] in TONES else "unclear"
  return label, tone

