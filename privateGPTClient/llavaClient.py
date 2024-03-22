import ollama


def describe_image(id, prompt: str, images: list):
    res = ollama.chat(
        model="llava:latest",
        messages=[
            {
                'role': id,
                'content': prompt,
                'images': images
            }
        ]
    )

    response = res['message']['content']
    return response

reply = describe_image("user", "Extract the content from the license plate?", ['database/images/tesla.jpg'])
print(reply)
