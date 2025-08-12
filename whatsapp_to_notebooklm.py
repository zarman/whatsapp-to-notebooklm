import os
import re
import base64
from datetime import datetime
from pathlib import Path
import shutil
from collections import defaultdict

class WhatsAppToNotebookLM:
    def __init__(self, chat_folder_path, output_folder_path):
        self.chat_folder = Path(chat_folder_path)
        self.output_folder = Path(output_folder_path)
        self.output_folder.mkdir(exist_ok=True)
        
        # Supported image formats for embedding as base64
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        # NotebookLM supported media formats that should be separate files
        self.audio_video_extensions = {'.3g2', '.3gp', '.aac', '.aif', '.aifc', '.aiff', 
                                     '.amr', '.au', '.avi', '.cda', '.m4a', '.mid', 
                                     '.mp3', '.mp4', '.mpeg', '.ogg', '.opus', '.ra', 
                                     '.ram', '.snd', '.wav', '.wma'}
        
        # Document formats
        self.document_extensions = {'.pdf', '.txt', '.md'}
        
        # Find the chat text file
        self.chat_file = self.find_chat_file()
        
    def find_chat_file(self):
        """Find the WhatsApp chat text file"""
        txt_files = list(self.chat_folder.glob("*.txt"))
        if not txt_files:
            raise FileNotFoundError("No .txt file found in the chat folder")
        
        # Usually the chat file is the largest txt file or has "WhatsApp Chat" in name
        chat_file = max(txt_files, key=lambda f: f.stat().st_size)
        print(f"Using chat file: {chat_file.name}")
        return chat_file
    
    def parse_whatsapp_date(self, line):
        """Extract date from WhatsApp message line"""
        # Common WhatsApp date patterns
        patterns = [
            r'(\d{1,2}/\d{1,2}/\d{2,4}),\s*\d{1,2}:\d{2}',  # MM/DD/YY or MM/DD/YYYY
            r'(\d{1,2}/\d{1,2}/\d{2,4})\s*\d{1,2}:\d{2}',   # Without comma
            r'(\d{4}-\d{2}-\d{2})\s*\d{2}:\d{2}',           # YYYY-MM-DD
            r'(\d{1,2}\.\d{1,2}\.\d{2,4}),\s*\d{1,2}:\d{2}', # DD.MM.YY
            r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*\d{1,2}:\d{2}', # [MM/DD/YY format
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line.strip())
            if match:
                date_str = match.group(1)
                try:
                    # Try different date formats
                    for fmt in ['%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d.%m.%Y', '%d.%m.%y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except ValueError:
                    pass
        return None
    
    def get_image_markdown(self, filename):
        """Convert image to base64 markdown format"""
        media_path = self.chat_folder / filename
        if not media_path.exists():
            return f"![Image not found: {filename}]"
        
        try:
            with open(media_path, 'rb') as f:
                base64_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Get MIME type
            ext = Path(filename).suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                '.png': 'image/png', '.gif': 'image/gif',
                '.bmp': 'image/bmp', '.webp': 'image/webp'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            
            # Return markdown image with base64 data
            return f"![{filename}](data:{mime_type};base64,{base64_data})"
            
        except Exception as e:
            print(f"Error encoding {filename}: {e}")
            return f"![Error loading image: {filename}]"
    
    def find_media_references(self, line):
        """Find media file references in a line of text"""
        media_files = []
        
        # Check if line contains any filenames that exist in the folder
        for file_path in self.chat_folder.iterdir():
            if file_path.is_file() and file_path.name != self.chat_file.name:
                if file_path.name in line:
                    media_files.append(file_path.name)
        
        return media_files
    
    def process_chat(self):
        """Main processing function"""
        print("Reading chat file...")
        
        with open(self.chat_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Group messages by month
        monthly_messages = defaultdict(list)
        current_month = None
        current_message = []
        
        print("Parsing messages by month...")
        
        for line in lines:
            # Check if this is a new message (starts with date)
            parsed_date = self.parse_whatsapp_date(line)
            
            if parsed_date:
                # Save previous message if exists
                if current_message and current_month:
                    monthly_messages[current_month].extend(current_message)
                
                # Start new message
                current_month = parsed_date.strftime("%Y-%m")
                current_message = [line]
            else:
                # Continuation of current message
                if current_message:
                    current_message.append(line)
        
        # Don't forget the last message
        if current_message and current_month:
            monthly_messages[current_month].extend(current_message)
        
        print(f"Found {len(monthly_messages)} months of data")
        
        # Process each month
        for month, messages in monthly_messages.items():
            print(f"Processing {month}...")
            self.create_monthly_files(month, messages)
        
        print("Processing complete!")
    
    def create_monthly_files(self, month, messages):
        """Create markdown files for one month"""
        # Create markdown file for the month with descriptive name
        year, month_num = month.split('-')
        month_names = {
            '01': 'January', '02': 'February', '03': 'March', '04': 'April',
            '05': 'May', '06': 'June', '07': 'July', '08': 'August',
            '09': 'September', '10': 'October', '11': 'November', '12': 'December'
        }
        month_name = month_names.get(month_num, f"Month{month_num}")
        markdown_file = self.output_folder / f"WhatsApp_Chat_{month_name}_{year}.md"
        
        markdown_content = f"# WhatsApp Chat - {month_name} {year}\n\n"
        markdown_content += f"*Generated from WhatsApp export*\n\n"
        markdown_content += f"**Period:** {month_name} {year}\n\n"
        markdown_content += "---\n\n"
        
        media_files_copied = []
        
        for line in messages:
            line = line.strip()
            if not line:
                continue
            
            # Find media references in this line
            media_files = self.find_media_references(line)
            
            # Process the line
            processed_line = line
            
            # Handle found media files
            for media_file in media_files:
                file_ext = Path(media_file).suffix.lower()
                
                if file_ext in self.image_extensions:
                    # Embed images directly in markdown
                    image_markdown = self.get_image_markdown(media_file)
                    processed_line = processed_line.replace(media_file, f"\n\n{image_markdown}\n\n*Image: {media_file}*\n")
                
                elif file_ext in self.audio_video_extensions:
                    # Reference audio/video files but don't copy them
                    file_type = "Audio" if file_ext in {'.aac', '.aif', '.aifc', '.aiff', '.amr', '.au', '.cda', '.m4a', '.mid', '.mp3', '.ogg', '.opus', '.ra', '.ram', '.snd', '.wav', '.wma'} else "Video"
                    processed_line = processed_line.replace(media_file, f"\n\n**📹 {file_type} content sent: {media_file}**\n*({file_type} content not uploaded to NotebookLM)*\n")
                
                elif file_ext in self.document_extensions:
                    # Reference document files but don't copy them
                    processed_line = processed_line.replace(media_file, f"\n\n**📄 Document sent: {media_file}**\n*(Document content not uploaded to NotebookLM)*\n")
                
                else:
                    # Unsupported format - just mention it
                    processed_line = processed_line.replace(media_file, f"\n\n**File: {media_file} (unsupported format for NotebookLM)**\n")
            
            # Handle generic media omitted messages
            media_omitted_patterns = [
                (r'<Media omitted>', "**[Media content omitted]**"),
                (r'\[Media omitted\]', "**[Media content omitted]**"),
                (r'<attached: (.+?)>', r"**[Attachment: \1]**"),
                (r'\(file attached\)', "**[File attached]**"),
            ]
            
            for pattern, replacement in media_omitted_patterns:
                processed_line = re.sub(pattern, replacement, processed_line, flags=re.IGNORECASE)
            
            # Add the processed line to markdown (escape special markdown characters in the text part)
            if processed_line != line:  # If we made changes, it likely has media
                markdown_content += processed_line + "\n\n"
            else:
                # Escape markdown special characters for regular text
                escaped_line = processed_line.replace('*', '\\*').replace('_', '\\_').replace('#', '\\#')
                markdown_content += escaped_line + "\n\n"
        
        # Add summary of media files at the end
        if media_files_copied:
            markdown_content += "\n---\n\n## Media Content Summary\n\n"
            markdown_content += f"This chat contained various media files that were referenced but not uploaded to NotebookLM:\n\n"
            markdown_content += "- **Images**: Embedded directly in this document\n"
            markdown_content += "- **Videos/Audio/Documents**: Referenced by filename only\n\n"
        
        # Write markdown file
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Created: {markdown_file.name}")

def get_folder_path(prompt_text):
    """Get folder path from user with validation"""
    while True:
        folder_path = input(f"\n{prompt_text}\nPath: ").strip()
        
        # Remove quotes if user added them
        folder_path = folder_path.strip('"\'')
        
        # Convert to Path object
        path = Path(folder_path)
        
        if path.exists() and path.is_dir():
            return str(path)
        else:
            print(f"❌ Error: The folder '{folder_path}' doesn't exist or is not a folder.")
            print("Please enter a valid folder path.")

def main():
    """Main function with user-friendly interface"""
    print("=" * 60)
    print("           WhatsApp Chat to NotebookLM Converter")
    print("=" * 60)
    print()
    print("This tool converts your WhatsApp chat export into markdown files")
    print("that can be uploaded to NotebookLM for AI-powered chat analysis.")
    print()
    print("What you'll need:")
    print("- A WhatsApp chat export folder (containing .txt file and media)")
    print("- A destination folder where the converted files will be saved")
    print()
    
    # Get input folder
    print("📂 STEP 1: WhatsApp Export Folder")
    print("This should be the folder containing your WhatsApp chat export")
    print("(it will have a .txt file and media files)")
    chat_folder = get_folder_path("Enter the path to your WhatsApp export folder:")
    
    # Get output folder
    print("\n📁 STEP 2: Output Folder")
    print("This is where the converted markdown files will be saved")
    print("(the folder will be created if it doesn't exist)")
    
    while True:
        output_folder = input("\nEnter the path for your output folder:\nPath: ").strip()
        output_folder = output_folder.strip('"\'')
        
        try:
            output_path = Path(output_folder)
            output_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Output folder ready: {output_path}")
            break
        except Exception as e:
            print(f"❌ Error creating folder: {e}")
            print("Please enter a valid folder path.")
    
    print("\n🚀 STEP 3: Processing")
    print("Starting conversion...")
    print()
    
    try:
        # Create converter instance
        converter = WhatsAppToNotebookLM(chat_folder, output_folder)
        
        # Process the chat
        converter.process_chat()
        
        print(f"\n✅ SUCCESS! Processing complete!")
        print(f"📁 All files created in: {output_folder}")
        
        # Show created files
        output_path = Path(output_folder)
        if output_path.exists():
            md_files = list(output_path.glob("*.md"))
            
            print(f"\n📄 Created {len(md_files)} markdown files:")
            for md_file in sorted(md_files):
                print(f"   - {md_file.name}")
        
        print("\n🎉 NEXT STEPS:")
        print("1. Go to https://notebooklm.google.com")
        print("2. Create a new notebook")
        print("3. Upload all the markdown (.md) files from your output folder")
        print("4. Start asking questions about your WhatsApp conversations!")
        print()
        print("💡 TIPS:")
        print("- Images are embedded directly in the markdown files")
        print("- You can ask questions like 'What happened in January 2024?'")
        print("- Videos/audio/documents are referenced but not uploaded")
        print("- Each month is a separate file for faster searching")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPlease check:")
        print("- The WhatsApp export folder contains a .txt file")
        print("- You have write permissions to the output folder")
        print("- The folder paths are correct")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
