import asyncio

from pptx import Presentation
import os
import openai
import json

ERROR_MESSAGE = "Something is wrong: "
openai.api_key = os.environ.get('API_KEY')


# C:\Users\User\Downloads\End of course exercise - kickof - upload (1).pptx
# C:\Users\User\Desktop\bigDataSeminar\recommendationSystems.pptx


def validatePath(path):
    """
    this method receives a path and validates if the path is valid or not, if not it provides
    a message to the user and asks him again for a new path, this procedure is repeated until the user
    provides a valid power-point path.
    :param path: path to power-point presentation file
    :return: returns all the data in the power-point
    """
    presentation = None

    if os.path.exists(path):  # check if the path exists
        try:
            presentation = Presentation(path)  # check if the path is a power-point path
        except Exception as e:  # throw exception if encountered an error
            print(ERROR_MESSAGE + "the path provided is not valid")
            raise e
    else:
        print(ERROR_MESSAGE + "the path provided does not exist")

    return presentation


def parsePptx(prs):
    """
    this method receives the presentation and parses the data into a suitable data structure, it first stores
    the number of the slide, then the title of the slide, (some pptx slides don't have titles, if so, instead we write
    Untitled slides to prevent errors), and then it extracts all the contents in the slide.
    :param prs: a valid presentation file
    :return: returns the data structure that contains all the parsed data
    """
    slide_data = {}

    for slide_index, slide in enumerate(prs.slides):
        slide_dict = {}

        try:
            slide_dict['title'] = slide.title.text
        except AttributeError:
            slide_dict['title'] = "Untitled Slide"

        slide_content = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        slide_content.append(run.text.strip())

        slide_dict['content'] = slide_content
        slide_data[f"Slide {slide_index + 1}"] = slide_dict

    return slide_data


def get_presentation_title():
    return input("Please enter the presentation's title: ")


def get_presentation_path():
    return input("Please provide the path of the PowerPoint you want to be explained: ")


def handleInput():
    """
    this method loops until the user provides valid input, it first asks for the title of the presentation, then
    asks for the path, validates the path, parses the data to make it ready for the AI requests.
    :return: data structure container: title, path and the parsed data.
    """
    while True:
        presentaion_title = get_presentation_title()
        pptxPath = get_presentation_path()
        input_data = {
            "title": presentaion_title,
            "path": pptxPath,
        }
        prs = validatePath(input_data['path'])
        if prs:
            slide_data = parsePptx(prs)
            input_data.update({'slide_data': slide_data})
            return input_data


def create_prompt(slide_data, presentation_title):
    """
    this method receives the parsed data and the title of the presentation, builds a suitable prompt to send
    to the ai engine. the title is used in every slide in order to maintain the main subject of the presentation.
    whereas the parsed data shows the specific aspects of those subjects
    :param slide_data: parsed slides
    :param presentation_title: title of the presentation
    :return:
    """
    prompts = []

    introduction = f"I have this PowerPoint presentation titled '{presentation_title}', and it covers various topics." \
                   f"Let's dive into the slides:\n"
    prompts.append(introduction)  # build the intro of the prompt

    for slide_title, slide_info in slide_data.items():
        slide_content = " ".join(slide_info['content'])
        slide_prompt = f"Slide '{slide_title}': {slide_info['title']}\n{slide_content}"
        prompts.append(slide_prompt)  # then build the body of the prompt

    return prompts


async def request_completion(prompt):
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Can you explain this to me in basic english?"},
        ],
    )
    return response["choices"][0].message.content


async def generateExplanations(prompts):
    explanations = {}
    tasks = []

    async def fetch_explanation(prompt, slide_index):
        response = await request_completion(prompt)
        explanations[f"Slide {slide_index + 1}"] = response

    for slide_index, prompt in enumerate(prompts):
        task = asyncio.create_task(fetch_explanation(prompt, slide_index))
        tasks.append(task)

    await asyncio.gather(*tasks)

    return explanations


def cleanExplanations(explanations):
    cleaned_explanations = {
        slide_title: explanation.replace('\n', '')
        for slide_title, explanation in explanations.items()
    }
    return cleaned_explanations


async def saveExplanations(explanations):
    output_file = "explanations.json"
    cleaned_explanations = cleanExplanations(explanations)

    with open(output_file, "w") as file:
        json.dump(cleaned_explanations, file, indent=4)

    print(f"Explanations saved to {output_file}")


async def main():
    slide_data = handleInput()
    prompts = create_prompt(slide_data["slide_data"], slide_data["title"])
    explanations = await generateExplanations(prompts)  # Await explanations generation
    await saveExplanations(explanations)


if __name__ == '__main__':
    asyncio.run(main())
