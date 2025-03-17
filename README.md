# Recast
A NovelAi tool that helps you improve the quality of your generated text. Fanmade.

# HOW TO INSTALL RECAST
Follow the steps carefully in the order presented, and you should be fine. If you get stuck, please don't hesitate to ask me for help! 

**What you'll need:**
- **Python:** Recast needs Python to run. (At least for now) If you don't have it already, you'll need to install it. You can download it from here: [https://www.python.org/downloads/](https://www.google.com/url?sa=E&q=https%3A%2F%2Fwww.python.org%2Fdownloads%2F)
    
    - **Important:** When you download Python, make sure to check the box that says "Add Python to PATH" during the installation. This is very important!
       
- **Download & unzip** I've uploaded a file called "Recast". You'll need to extract (unzip or use Winrar) all the files from this archive to a folder on your computer. e.g., creating a new folder on your Desktop or D: called 'Recast NovelAI' or something like that and extracting the files there.    

**Installation of dependencies:**
1. **Open the Command Prompt (Windows) or Terminal (Mac/Linux):**
    - **Windows:** Press the Windows key, type "cmd", and press Enter. A black window will open.
   
    - **Mac:** Open the "Terminal" application. You can find it in Applications > Utilities.

    - **Linux:** The Terminal application is usually in your applications menu. It might be called "Terminal," "Console," or something similar but, if you use Linux, you should be already familiar.

2. **Navigate to the Program Folder:** You need to tell the command prompt/terminal to go to the folder where you extracted my program files. Use the cd command (which stands for "change directory").
    
    - **Example:** If you extracted the files to a folder called "Recast" on your Desktop, you would type this and press Enter:
        
        ```
        cd Desktop/Recast
        ```        
3. **Install the Required Libraries:** Now, you are in the right place & need to install the extra pieces of software that Recast needs. Type this command and press Enter:
 
    ```
    pip install -r requirements.txt
    ```

    - This will download and install everything automatically. You'll see a lot of text scrolling by. Don't worry about it unless you see an error message.

4. **Run the Program:** Once the installation is finished, you should be able to run Recast. Type this command and press Enter, or JUST DOUBLE CLIK ON THE "Recast.py" file in the folder.

    ```
    python Recast.py
    ```


**Troubleshooting:**
- **"pip" is not recognized:** If you get an error message saying "pip" is not recognized, it means Python wasn't added to your PATH correctly during installation. You might need to reinstall Python and make sure to check the "Add Python to PATH" box.
- **Other Errors:** If you see any other error messages, please upload a screenshot, and I'll do my best to help you figure it out.
