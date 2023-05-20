from pptx import Presentation
import os
import openai
import asyncio
import json

ERRORMSG = "Something is wrong: "
API_KEY = "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"

# C:\Users\User\Downloads\End of course exercise - kickof - upload (1).pptx
# C:\Users\User\Desktop\bigDataSeminar\recommendationSystems.pptx


def validatePath(path):
    presentation = None

    if os.path.exists(path):
        try:
            presentation = Presentation(path)
        except Exception as e:
            print(ERRORMSG + "the path provided is not valid")
            raise e
    else:
        print(ERRORMSG + "the path provided does not exist")

    return presentation


def parsePptx(prs):
    slide_data = {}

    for slide_index, slide in enumerate(prs.slides):
        slide_dict = {}

        try:
            slide_dict['title'] = slide.title.text
        except AttributeError:
            slide_dict['title'] = "Untitled Slide"

        slide_content = [
            paragraph.text
            for shape in slide.shapes
            if shape.is_placeholder and shape.has_text_frame
            for paragraph in shape.text_frame.paragraphs
        ]

        slide_dict['content'] = slide_content
        slide_data[f"Slide {slide_index + 1}"] = slide_dict

    return slide_data


def handleInput():
    while True:
        presentaion_title = input("Please enter the presentation's title: ")
        pptxPath = input("Please provide the path of the PowerPoint you want to be explained: ")
        input_data = {
            "title": presentaion_title,
            "path": pptxPath,
        }
        prs = validatePath(input_data['path'])
        if prs:
            slide_data = parsePptx(prs)
            input_data.update({'slide_data': slide_data})
            return input_data


def createPrompt(slide_data, presentation_title):
    prompts = []
    introduction = f"I have this PowerPoint presentation titled '{presentation_title}', and it covers various topics. " \
                   f"Let's dive into the slides:\n"
    prompts.append(introduction)

    for slide_title, slide_info in slide_data.items():
        slide_content = " ".join(slide_info['content'])
        slide_prompt = f"Slide '{slide_title}': {slide_info['title']}\n{slide_content}"
        prompts.append(slide_prompt)

    return prompts


def request_from_api(prompt):
    openai.api_key = API_KEY
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()


def generateExplanations(prompts):
    explanations = {}
    for slide_index, prompt in enumerate(prompts):
        response = request_from_api(prompt)
        explanations[f"Slide {slide_index + 1}"] = response
    return explanations


def saveExplanations(explanations):
    output_file = "explanations.json"
    with open(output_file, "w") as file:

        cleaned_explanations = {
            slide_title: explanation.replace('\n', '')
            for slide_title, explanation in explanations.items()
        }
        json.dump(cleaned_explanations, file, indent=4)

    print(f"Explanations saved to {output_file}")


def main():
    slide_data = handleInput()
    prompts = createPrompt(slide_data["slide_data"], slide_data["title"])
    explanations = generateExplanations(prompts)
    saveExplanations(explanations)


if __name__ == '__main__':
    main()
