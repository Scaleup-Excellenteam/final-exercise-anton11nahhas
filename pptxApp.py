from pptx import Presentation
import os


ERRORMSG = "Something is wrong: "


def validatePath(path):
    if os.path.exists(path):
        try:
            presentation = Presentation(path)
        except:
            print(ERRORMSG + "the path provided is not valid")
            handleInput()
    else:
        print(ERRORMSG + "the path provided does not exist")

    return presentation





def handleInput():
    pptxPath = input("Please provide the path of the PowerPoint you want to be explained: ")
    prs = validatePath(pptxPath)
    #parsePptx(prs)



def main():
    handleInput()


if __name__ == '__main__':
    main()