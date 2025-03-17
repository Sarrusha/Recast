# Recast
A NovelAi tool that helps you improve the quality of your generated text. Fanmade. 

# Status: Alpha Preview

### Require an active NovelAI subscription, https://novelai.net. Kayra is available for all tiers, Erato only for Opus. Quality of Erato is immeasurably superior, as is its ability to execute orders and commands. It is highly recommended to have Opus as a subscription.

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

4.**Credentials:** Recast uses the same credentials that you use to log in in the NovelAI website. In the Recast folder, you can see a file called credentials.json. Open it with notepad, openoffice, word or any text processor and insert your username or email (like name@gmail.com) and password for the site inside the quotation marks. 
    Save. *Note:* Do NOT insert your credentials if you use a machine that anyone can access outside of you, because they can just open the file and read them. Trust it like a plain, regular .txt file with your password inside. This is just temporary and & will be addressed briefly in the next patch.

5.**Run the Program:** Now, you should be able to run Recast. Type this command and press Enter, or JUST DOUBLE CLIK ON THE "Recast.py" file in the folder.

    ```
    python Recast.py
    ```


**Troubleshooting:**
- **"pip" is not recognized:** If you get an error message saying "pip" is not recognized, it means Python wasn't added to your PATH correctly during installation. You might need to reinstall Python and make sure to check the "Add Python to PATH" box.
- **Other Errors:** If you see any other error messages, please upload a screenshot, and I'll do my best to help you figure it out.

TODO:
- Salt & crypt the credentials.
- Make a simple .exe for not tech people.

Note: This is NOT an official program made by Anlatan. It is a labor of love from a fan of their work. 

### Credits:
Aedial repository, without which this work would not exist:
https://github.com/Aedial/novelai-api

