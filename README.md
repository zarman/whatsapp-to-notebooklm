# WhatsApp to NotebookLM Converter

Convert your WhatsApp chat exports into NotebookLM-ready markdown files for AI-powered conversation analysis.

## 🎯 What This Does

This tool takes your WhatsApp chat export and converts it into organized markdown files that you can upload to [Google's NotebookLM](https://notebooklm.google.com) to ask AI questions about your conversations.

### ✨ Features

- **📅 Monthly Organization**: Splits your chat into monthly files for faster NotebookLM processing
- **🖼️ Embedded Images**: Images appear directly inline with your conversations  
- **📹 Media References**: Videos, audio, and documents are noted but not uploaded (to stay under file limits)
- **🎯 AI-Ready**: Formatted specifically for NotebookLM's requirements
- **🚀 Easy to Use**: Interactive interface - just run and follow the prompts

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- A WhatsApp chat export (see [How to Export](#how-to-export-whatsapp-chat) below)

### Installation

1. **Download the script**:
   - Click the green "Code" button above
   - Select "Download ZIP"
   - Extract the ZIP file to a folder

2. **Run the converter**:
   ```bash
   python whatsapp_to_notebooklm.py
   ```

3. **Follow the prompts**:
   - Enter your WhatsApp export folder path
   - Choose where to save the converted files
   - Wait for processing to complete

4. **Upload to NotebookLM**:
   - Go to [notebooklm.google.com](https://notebooklm.google.com)
   - Create a new notebook
   - Upload all the generated markdown files
   - Start asking questions!

## 📱 How to Export WhatsApp Chat

### On iPhone:
1. Open the chat you want to export
2. Tap the contact/group name at the top
3. Scroll down and tap "Export Chat"
4. Choose "Attach Media" for complete export
5. Save to Files app

### On Android:
1. Open the chat you want to export
2. Tap the three dots menu (⋮)
3. Select "More" → "Export chat"
4. Choose "Include media"
5. Save to your device

## 💡 What You Get

The converter creates files like this:

```
📁 Output Folder/
├── WhatsApp_Chat_January_2024.md
├── WhatsApp_Chat_February_2024.md
├── WhatsApp_Chat_March_2024.md
└── ...
```

Each markdown file contains:
- **All text messages** for that month
- **Images embedded directly** (displayed inline)
- **References to videos/audio/documents** (filename noted but not uploaded)
- **Clean formatting** optimized for AI analysis

## 🤖 Using with NotebookLM

Once you upload the files to NotebookLM, you can ask questions like:

- *"What did we talk about in March 2024?"*
- *"Show me all the images from our vacation"*  
- *"Summarize the main topics from last year"*
- *"When did we discuss buying a house?"*
- *"What videos were shared in December?"*

## 🔧 Troubleshooting

### Common Issues:

**"No .txt file found"**
- Make sure you exported the chat "with media" 
- Check that the export folder contains a .txt file

**"Permission denied"**
- Make sure you can write to the output folder
- Try running as administrator if needed

**"Images not showing"**
- Large images might take time to process
- Very large exports might hit memory limits

### Need Help?

- Check the [Issues](../../issues) page for common problems
- Create a new issue if you need help

## 📝 Technical Details

### Supported File Types:

- **Images**: JPG, PNG, GIF, BMP, WebP (embedded in markdown)
- **Videos**: MP4, AVI, MOV, 3GP, MPEG (referenced only)
- **Audio**: MP3, AAC, WAV, M4A, OGG, AMR (referenced only) 
- **Documents**: PDF, TXT, MD (referenced only)

### Why Not Upload All Media?

NotebookLM has a 50-file limit per notebook. With hundreds of media files in typical WhatsApp exports, we:
- Embed images directly (unlimited)
- Reference other media by filename (preserves context)
- Keep under the file limit while maintaining usability

## 🤝 Contributing

Found a bug or have a suggestion? 

1. Check the [Issues](../../issues) page first
2. Create a new issue with details
3. Pull requests are welcome!

## ⚖️ Privacy & Security

- This tool runs completely on your local machine
- No data is sent to any servers
- Your chat exports never leave your computer
- Generated files are saved locally for you to upload

## 📄 License

MIT License - feel free to use, modify, and share!
