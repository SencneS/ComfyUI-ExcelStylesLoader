ComfyUI Styles loader (Excel Edition)

Node ispired by - https://github.com/theUpsider/ComfyUI-Styles_CSV_Loader - Thank you for your creation, I used it quiet a lot, but I needed more :)
Created for Ideogram 4 Settings Node

\# ComfyUI Excel Styles Loader

A self-contained custom node for ComfyUI that dynamically reads styles from individual tabs/sheets within an Excel workbook (`styles.xlsx`).

It has the Styles sheet from A1111 but it also has additional tabs for Ideogram 4's prompt nodes.
I've also added the functions for Krea2 (using the same Ideogram 4 node).

What I did was look up what Ideogram4 and Krea2 nativily support in each settings, used Gemini to help with this along with looking at each UNETs metadata and documentation.
Art_Style
Aesthetics
Lighting
Medium

I have tags for each setting ID = Ideogram4, K2 = Krea2. (I might put them in separate tabs in the style sheet later)

\## Installation

\### Method 1: Manual Git Clone

1\. Open your terminal or command prompt in your ComfyUI folder

2\. cd ComfyUI/custom\_nodes

3\. git clone https://github.com/SencneS/ComfyUI-ExcelStylesLoader.git

4\. cd ComfyUI-ExcelStylesLoader

5\. pip instal -r requirements.txt

6\. Restart ComfyIU

\### Method 2: Install via ComfyUI Manager.

1. Find the Excel Styles loader and install.
2. Restart ComfyUI

\# Excel Style's update.

It's very simple - Each Tab represnets a separate drop-down section on the Node.
So you can split this up into a lot of different categories if you really wanted to.
You can create your very own tab if you want, when you save the file into the node folder, press "R" on comfy and it'll add the new styles or remove them or edit them on the fly.

You don't need to use this for Styles. Someone reached out to me telling me they're using this as a drop-down positive and negative prompts!

Enjoy.

p.s. Yeah I suck at GITHubbing, I'm not a coder, everything about this was created by Vibe Coding with Gemini :)
So I don't have a pretty ReadMe LOL
