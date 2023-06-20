# -----------------------------MODULE SECTION-------------------------------------------------------------------
import time
from pptx import Presentation
import openai
import json
import os
import re
import asyncio

# -----------------------------CONSTANT SECTION-------------------------------------------------------------------
openai.api_key = os.environ.get('API_KEY')
CONTENT = [
    {"role": "system", "content": "Can you explain the slides in basic english, and provide examples if needed!"}
]
ERROR_MESSAGE = "Something is wrong:"
ENGINE_MODEL = "gpt-3.5-turbo"


# -----------------------------METHOD SECTION-------------------------------------------------------------------
async def parse_presentation(presentation_path):
    """
    this method receives a path for a pptx presentation, checks if the path is found in the operating system, if so,
    parses the data to slides. the method, returns a list of explanations.
    :param: presentation_path: path of a power-point presentation (String)
    :return: list of explanations (List of strings)
    """
    if not os.path.isfile(presentation_path):  # check if path is available
        print(f"{ERROR_MESSAGE} the path you provided does not exist.")
        return []

    prs = Presentation(presentation_path)
    explanations = []
    for slide in prs.slides:
        explanation = await parse_slide_of_pptx(slide)  # call method to parse data in each slide
        explanations.append(explanation)
    return explanations


# --------------------------------------------------------------------------------------------------------------------
async def parse_slide_of_pptx(slide):
    """
    this method receives a single slide, the method parses the data on that slide, it calls another method to get the
    response and return it to the parse_presentation method. it throws an error if an exception occurred.
    :param: slide: a single slide from the power-point (slide object)
    :return: the explanation if the processing went well, an error, otherwise. (List of Strings)
    """
    try:
        response = await request_completion(slide)  # call a function to get explanations on each slide.
        return response
    except Exception as error:  # if an error occurred, display a suitable message to user.
        error_message = f"{ERROR_MESSAGE} Error processing slide: {str(error)}"
        return error_message


# --------------------------------------------------------------------------------------------------------------------
def parse_text_of_slide(slide):
    """
    this method receives a slide, and extracts all the extractable text found in that slide. In addition, it cleans
    the data using the strip function.
    :param: slide: a single slide from the power-point (Slide Object)
    :return: explanation response (String)
    """
    slide_text = []
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                slide_text.append(run.text.strip())
    return " ".join(slide_text)


# --------------------------------------------------------------------------------------------------------------------
async def request_completion(slide):
    """
    this method receives a slide object, sends a request to the openai API asking the server to explain the content
    of that slide, the method returns the response from the API
    :param: slide: slide: a single slide from the power-point (Slide Object)
    :return: response of the API
    """
    CONTENT.append({"role": "user", "content": parse_text_of_slide(slide)})
    response = await openai.ChatCompletion.acreate(
        model=ENGINE_MODEL,  # using the chat gpt-3.5-turbo model to get strong responses
        messages=CONTENT
    )
    content = response["choices"][0].message.content
    cleaned_content = clean_text(content)  # clean content from unwanted characters.
    return cleaned_content


# --------------------------------------------------------------------------------------------------------------------
def clean_text(text):
    """
    this method receives the response retrieved from the openai API and cleans it, in other words, gets rid of
    unwanted characters.
    :param: text: response from API (string)
    :return: clean version of the response (string)
    """
    cleaned_text = re.sub(r"\n", "", text)
    cleaned_text = cleaned_text.encode("ascii", "ignore").decode("utf-8")
    return cleaned_text.strip()


# --------------------------------------------------------------------------------------------------------------------
def save_explanations(explanations, presentation_path):
    """
    this method receives a list of strings each string implements an explanation, creates a JSON file and appends
    the explanations to the file, in the format of (slide#: explanations).
    :param: explanations: list of explanation retrieved from the API (List of strings)
    :return:
    """
    presentation_name = os.path.basename(presentation_path)  # get the base name of power-point from path
    presentation_name = os.path.splitext(presentation_name)[0]  # remove file's extension
    output_file = f"{presentation_name}_explanations.json"  # name the output file, with the name of power-point
    slide_explanations = {}

    for slide_num, explanation in enumerate(explanations, start=1):
        slide_key = f"slide{slide_num}"
        slide_explanations[slide_key] = explanation

    try:
        if not os.path.exists(output_file):  # create file if it does not exist.
            open(output_file, 'w').close()

        with open(output_file, 'w') as file:
            json.dump(slide_explanations, file, indent=4)
        print(f"Explanations saved to {output_file}")
    except IOError as error:
        print(f"{ERROR_MESSAGE} Error saving explanations: {str(error)}")


# --------------------------------------------------------------------------------------------------------------------
async def main(presentation_path):
    """
    this is the main method, uses asyncio handling to await the requests sent to the openai API, and handles saving
    the responses to the output file.
    :param: presentation_path: string of a power-point path. (string)
    :return:
    """
    explanations = await parse_presentation(presentation_path)
    save_explanations(explanations, presentation_path)


# --------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    the controller of the app, handles the inputs from the user, prints relevant messages and runs the main program
    """
    presentation_path = input("Please provide the path of the PowerPoint presentation: ")
    print("Processing PowerPoint...")  # inform the user to wait until the program finishes running
    start_time = time.time()  # compute time of execution

    asyncio.run(main(presentation_path))  # run main program

    end_time = time.time()
    execution_time = end_time - start_time
    minutes, seconds = divmod(execution_time, 60)
    print(f"Execution time: {minutes:.0f} minutes {seconds:.2f} seconds")  # print total time of execution
