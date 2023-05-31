import time
from pptx import Presentation
import openai
import json
import os
import re
import asyncio

openai.api_key = os.environ.get('API_KEY')
CONTENT = [
    {"role": "system", "content": "Can you explain the slides in basic english, and provide examples if needed!"}
]
ERROR_MESSAGE = "Something is wrong:"
ENGINE_MODEL = "gpt-3.5-turbo"
WRITE_TO_FILE_MODE = 'w'


async def parse_presentation(presentation_path):
    """
    This method receives a path for a pptx presentation, checks if the path is found in the operating system, if so,
    parses the data to slides. The method, returns a list of explanations.
    :param: presentation_path: path of a power-point presentation. (String)
    :return: list of explanations. (List of strings)
    """
    # check if path is available
    if not os.path.isfile(presentation_path):
        print(f"{ERROR_MESSAGE} the path you provided does not exist.")
        return []

    prs = Presentation(presentation_path)
    explanations = []
    for slide in prs.slides:
        explanation = await parse_slide_of_pptx(slide)
        explanations.append(explanation)
    return explanations


async def parse_slide_of_pptx(slide):
    """
    This method receives a single slide, the method parses the data on that slide, it calls another method to get the
    response and return it to the parse_presentation method. It throws an error if an exception occurred.
    :param: slide: A single slide from the power-point. (slide object)
    :return: The explanation if the processing went well, an error, otherwise. (List of Strings)
    """
    try:
        response = await request_completion(slide)
        return response
    except Exception as error:
        error_message = f"{ERROR_MESSAGE} Error processing slide: {str(error)}"
        return error_message


def parse_text_of_slide(slide):
    """
    This method receives a slide, and extracts all the extractable text found in that slide. In addition, it cleans
    the data using the strip function.
    :param: slide: A single slide from the power-point. (Slide Object)
    :return: Explanation response. (String)
    """
    slide_text = []
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                slide_text.append(run.text.strip())
    return " ".join(slide_text)


async def request_completion(slide):
    """
    This method receives a slide object, sends a request to the openai API asking the server to explain the content
    of that slide, the method returns the response from the API.
    :param: slide: Slide: a single slide from the power-point. (Slide Object)
    :return: Response of the API.
    """
    CONTENT.append({"role": "user", "content": parse_text_of_slide(slide)})
    response = await openai.ChatCompletion.acreate(
        model=ENGINE_MODEL,
        messages=CONTENT
    )
    content = response["choices"][0].message.content
    cleaned_content = clean_text(content)
    return cleaned_content


def clean_text(text):
    """
    This method receives the response retrieved from the openai API and cleans it, in other words, gets rid of
    unwanted characters.
    :param: text: Response from API. (string)
    :return: clean Version of the response. (string)
    """
    cleaned_text = re.sub(r"\n", "", text)
    cleaned_text = cleaned_text.encode("ascii", "ignore").decode("utf-8")
    return cleaned_text.strip()


def save_explanations(explanations, presentation_path):
    """
    This method receives a list of strings each string implements an explanation, creates a JSON file and appends
    the explanations to the file, in the format of (slide#: explanations).
    :param: explanations: List of explanation retrieved from the API. (List of strings)
    :return:
    """
    # get the base name of power-point from path
    presentation_name = os.path.basename(presentation_path)
    # remove file's extension
    presentation_name = os.path.splitext(presentation_name)[0]
    # name the output file, with the name of power-point
    output_file = f"{presentation_name}_explanations.json"
    slide_explanations = {}

    for slide_num, explanation in enumerate(explanations, start=1):
        slide_key = f"slide{slide_num}"
        slide_explanations[slide_key] = explanation

    try:
        if not os.path.exists(output_file):
            open(output_file, WRITE_TO_FILE_MODE).close()

        with open(output_file, WRITE_TO_FILE_MODE) as file:
            json.dump(slide_explanations, file, indent=4)
        print(f"Explanations saved to {output_file}")
    except IOError as error:
        print(f"{ERROR_MESSAGE} Error saving explanations: {str(error)}")


async def main(presentation_path):
    """
    This is the main method, uses asyncio handling to await the requests sent to the openai API, and handles saving
    the responses to the output file.
    :param: presentation_path: string of a power-point path. (string)
    :return:
    """
    explanations = await parse_presentation(presentation_path)
    save_explanations(explanations, presentation_path)


def get_input():
    """
    The method asks the user for a valid path.
    :return: Return the input provided by user.
    """
    input_message = "Please provide the path of the PowerPoint presentation: "
    return input(input_message)


if __name__ == "__main__":
    """
    The controller of the app, handles the inputs from the user, prints relevant messages and runs the main program.
    """
    presentation_path = get_input()
    print("Processing PowerPoint...")
    start_time = time.time()

    asyncio.run(main(presentation_path))

    end_time = time.time()
    execution_time = end_time - start_time
    minutes, seconds = divmod(execution_time, 60)
    print(f"Execution time: {minutes:.0f} minutes {seconds:.2f} seconds")
