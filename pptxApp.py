from pptx import Presentation
import os

ERRORMSG = "Something is wrong: "


# C:\Users\User\Downloads\End of course exercise - kickof - upload (1).pptx
# C:\Users\User\Desktop\bigDataSeminar\recommendationSystems.pptx
# for slide_title, slide_info in slide_data.items():
#     print("Slide:", slide_title)
#     print("Title:", slide_info['title'])
#     print("Content:")
#     for content in slide_info['content']:
#         print(content)
#     print()
# break

def validatePath(path):
    presentation = None

    if os.path.exists(path):
        try:
            presentation = Presentation(path)
        except Exception as e:
            print(ERRORMSG + "the path provided is not valid")
            raise e  # Raise the exception to be handled in the calling code
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

        slide_content = []

        for shape in slide.shapes:
            if shape.is_placeholder:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        slide_content.append(paragraph.text)

        slide_dict['content'] = slide_content

        slide_data[f"Slide {slide_index + 1}"] = slide_dict

    return slide_data


def handleInput():
    while True:
        pptxPath = input("Please provide the path of the PowerPoint you want to be explained: ")
        prs = validatePath(pptxPath)
        if prs:
            slide_data = parsePptx(prs)
            return slide_data


# for slide_title, slide_info in slide_data.items():
#     print("Slide:", slide_title)
#     print("Title:", slide_info['title'])
#     print("Content:")
#     for content in slide_info['content']:
#         print(content)
#     print()
def createPrompt(data):
    prompt_prefix = "So I have this Power Point Presentation that I got in class, I tried reading it and could not " \
                    "understand a thing, can you help understand it?"
    prompt_body = " "
    for slide_title, slide_info in data.items():
        prompt_body += f"Here is {slide_title}, and that is the title of the slide {slide_info['title']}, the slide " \
                       f"talks about {slide_info['content']}"

    return prompt_prefix + prompt_body


def main():
    parsed_data = handleInput()

    prompt = createPrompt(parsed_data)
    print(prompt)


if __name__ == '__main__':
    main()
