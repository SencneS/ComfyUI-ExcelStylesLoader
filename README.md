Created for Ideogram 4 Settings Node

\# ComfyUI Excel Styles Loader

A self-contained custom node for ComfyUI that dynamically reads styles from individual tabs/sheets within an Excel workbook (`styles.xlsx`).

It has the Styles sheet from A1111 but it also has additional tabs for Ideogram 4's prompt nodes.

\## Installation

\### Method 1: Manual Git Clone

1\. Open your terminal or command prompt.

2\. Navigate to your ComfyUI custom nodes path:

&#x20;  ```bash

&#x20;  cd ComfyUI/custom\_nodes

\### Method 2: Install via ComfyUI Manager.

1. Find the Excel Styles loader and install.
2. Restart ComfyUI

\# Excel Style's update.

It's very simple - Each Tab represnets a separate drop-down section.
So you can split this up into a lot of different categories if you really wanted to.

However, I did this to create text inputs via drop-downs according to each Ideogram 4 category.
