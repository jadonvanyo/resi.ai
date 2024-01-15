import os
import openai

# openai.api_key = "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"

# optional; defaults to `os.environ['OPENAI_API_KEY']`
openai.api_key = "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"

completion = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.choices[0].message.content)

# def chat_with_gpt(prompt):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": "Explain asynchronous programming in the style of the pirate Blackbeard."},
#         ],
#         temperature=0,
#     )
    
#     return response.choices[0].message.content.strip()

# if __name__ == "__main__":
#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ["end", "quit", "bye"]:
#             break
        
#     response = chat_with_gpt(user_input)
#     print("Chatbot: ", response)