from pptx import Presentation
import os
import openai
import asyncio
import json

ERRORMSG = "Something is wrong: "
API_KEY = " "  # NOTE: PLEASE PROVIDE YOUR API KEY HERE, IF I SHARE MINE IT GETS DISABLED!


# C:\Users\User\Downloads\End of course exercise - kickof - upload (1).pptx
# C:\Users\User\Desktop\bigDataSeminar\recommendationSystems.pptx


def validatePath(path):
    """
    this method receives a path and validates if the path is valid or not, if not it provides
    a message to the user and asks him again for a new path, this procedure is repeated until the user
    provides a valid powerpoint path.
    :param path: path to power point presentation file
    :return: returns all the data in the power-point
    """
    presentation = None

    if os.path.exists(path):  # check if the path exists
        try:
            presentation = Presentation(path)  # check if the path is a powerpoint path
        except Exception as e:  # throw exception if encountered an error
            print(ERRORMSG + "the path provided is not valid")
            raise e
    else:
        print(ERRORMSG + "the path provided does not exist")

    return presentation


def parsePptx(prs):
    """
    this method receives the presentation and parses the data into a suitable data structure, it first stores
    the number of the slide, then the title of the slide, (some pptx slides dont have titles, if so, instead we write
    Untitled slides to prevent errors), and then it extracts all of the contents in the slide.
    :param prs: a valid presentation file
    :return: returns the data structure that contains all of the parsed data
    """
    slide_data = {}

    for slide_index, slide in enumerate(prs.slides):  # loop through slides
        slide_dict = {}

        try:
            slide_dict['title'] = slide.title.text  # extract the title
        except AttributeError:
            slide_dict['title'] = "Untitled Slide"

        slide_content = [
            paragraph.text
            for shape in slide.shapes  # loop through the slides and extract texts
            if shape.is_placeholder and shape.has_text_frame
            for paragraph in shape.text_frame.paragraphs
        ]

        slide_dict['content'] = slide_content
        slide_data[f"Slide {slide_index + 1}"] = slide_dict

    return slide_data


def handleInput():
    """
    this method loops until the user provides valid input, it first asks for the title of the presentation, then
    asks for the path, calidates the path, parses the data to make it ready for the ai requests.
    :return: data structure container: title, path and the parsed data.
    """
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
    """
    this method receives the parsed data and the title of the presentation, builds a suitable prompt to send
    to the ai engine. the title is used in every slide in order to maintain the main subject of the presentation.
    whereas the parsed data shows the specific aspects of those subjects
    :param slide_data: parsed slides
    :param presentation_title: title of the presentation
    :return:
    """
    prompts = []
    introduction = f"I have this PowerPoint presentation titled '{presentation_title}', and it covers various topics. " \
                   f"Let's dive into the slides:\n"
    prompts.append(introduction)  # build the intro of the prompt

    for slide_title, slide_info in slide_data.items():
        slide_content = " ".join(slide_info['content'])
        slide_prompt = f"Slide '{slide_title}': {slide_info['title']}\n{slide_content}"
        prompts.append(slide_prompt)  # then build the body of the prompt

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
