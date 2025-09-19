# 📧 AI-Powered Email Assistant

## 🎯 Core Principle: Don't Replicate, Augment

Your app shouldn't try to be a better Gmail. It should be a **smart layer on top of Gmail** that uses AI to do things Gmail can't do easily.

---

## 🚀 Best Use Cases for Retrieving Gmail Content

### 1. 🎪 Context for AI Composition *(The Killer Feature)*

**How it works:** Your AI can read the last few emails in a conversation thread.

**The Value:** When a user says *"Reply to Sarah's last email,"* your AI knows exactly what Sarah said and can draft a context-perfect reply. This is infinitely more powerful than a blank slate.

---

### 2. 📊 Automated Email Triage & Summarization

**How it works:** Your app fetches new emails and uses your AI to summarize them, categorize them (e.g., "Urgent", "Project Apollo", "Newsletter"), or extract action items.

**The Value:** The user gets a daily/weekly digest from your app: 
> *"You have 12 new emails. 1 is urgent from your boss, 3 are about project planning, and the rest are newsletters."* 

This is a huge time-saver.

---

### 3. 🤝 Intelligent Contact Management *(Fits Your Current Feature)*

**How it works:** Your app scans the user's sent and received emails to automatically build and enrich their `email_name_maps` table. It finds names, email addresses, and even relationships (*"You email Tony every week, he's probably important"*).

**The Value:** Zero-effort contact building. The user never has to manually add "Joe" and "twilly.t@gmail.com" again.

---

### 4. 📈 Data Enrichment for Other Features

**How it works:** The content of emails becomes fuel for other AI tools. For example, an AI could analyze project-related emails and automatically generate a status report.

**The Value:** Turns the user's inbox from a passive pile of data into an active resource for insights.

---

## 🆚 Why This is Better Than "Just Using Gmail"

| Feature | In Gmail | In Your AI-Powered App |
|---------|----------|------------------------|
| **Replying** | You read, think, and type. | *"Reply to the last email from Tony and agree to the meeting time he suggested."* → **Done.** |
| **Finding Info** | You search, open emails, and read. | *"What did Sarah say about the project deadline last week?"* → AI finds and summarizes the relevant email. |
| **Managing Contacts** | You manually add contacts. | Your app automatically builds a rich contact list from all your conversations. |
| **Staying on Top** | You scan your inbox yourself. | You get a proactive, AI-generated briefing of what's important. |

---

## 🎯 Conclusion and Recommendation

### 🏆 **For your next step, focus on Use Case #1: Context for AI Composition.**

This aligns perfectly with what you've already built. It provides immediate, obvious value and will feel like **magic** to the user. 

### 🔄 The Workflow is Simple:

1. **User asks:** *"Reply to the last email from Jack Kruger."*

2. **Your app** uses the Gmail API to find the most recent email from Jack and pulls its content.

3. **Your AI** uses that content as context to draft a perfect, relevant reply.

4. **The drafted reply** appears in your composition window for the user to review and send.

---

## 💡 The Bottom Line

This isn't "yet another email client." This is a **productivity multiplier** that leverages your app's core strength: **AI**.

---

## 🛠️ Core LLM Toolset for Conversational Email Management

### 📂 Category 1: Core Fetch & Read Tools

#### 1. 📥 **fetch_emails**
- **Purpose:** Retrieves a list of new or filtered emails. This is the gateway tool.
- **Parameters:**
  - `max_results` (number): Limit results to avoid overload. Default: 10
  - `label` (string): Optional. Fetch from a specific label/folder (e.g., "INBOX", "UNREAD")
  - `query` (string): Optional. A Gmail search query (e.g., "from:boss subject:urgent")
- **AI's Goal:** Use this to see what's there, then guide the user on what to do next (summarize, read one-by-one, etc.)

#### 2. 📖 **get_email_content**
- **Purpose:** Fetches the full content, headers, and metadata of a specific email
- **Parameters:**
  - `email_id` (string): The Gmail ID of the email to read
- **AI's Goal:** Use this when the user wants to "read" a specific email. The AI should then read it aloud in the chat and immediately follow up with suggested actions (categorize, reply, archive)

---

### ⚡ Category 2: Single Email Action Tools

#### 3. 🏷️ **categorize_email**
- **Purpose:** Analyzes an email's content and context to assign a priority/status
- **Parameters:**
  - `email_id` (string): The Gmail ID of the email to categorize
  - `categories` (array): The list of categories to use. Default: ["HOT", "WARM", "COLD"]
- **AI's Goal:** Call this automatically after reading an email. Use the result to prompt the user: *"This is HOT because it's from your CEO about the quarterly report. Should we reply or snooze until tomorrow?"*

#### 4. ✍️ **generate_reply** *(CRITICAL)*
- **Purpose:** Drafts a reply based on the email's content and the user's instruction. This is the core of your AI's value
- **Parameters:**
  - `email_id` (string): The Gmail ID of the email to reply to
  - `user_instruction` (string): The user's desired intent (e.g., "say yes to the meeting", "ask for a deadline extension", "draft a polite decline")
  - `tone` (string): Optional. E.g., "professional", "casual", "urgent"
- **AI's Goal:** Generate the draft and present it to the user for approval (send, edit, cancel). **Do NOT send automatically**

#### 5. 🎯 **perform_email_action**
- **Purpose:** A general-purpose tool for common Gmail actions. Prevents tool bloat
- **Parameters:**
  - `email_id` (string): The Gmail ID of the target email
  - `action` (string): Must be one of: ["archive", "delete", "mark_as_read", "mark_as_unread", "snooze", "add_label"]
  - `label_name` (string): Required only if action is add_label
- **AI's Goal:** Execute the user's command (e.g., "archive it", "mark it as unread") and confirm it was done

---

### 📊 Category 3: Bulk Processing Tools

#### 6. 📋 **categorize_all_emails**
- **Purpose:** Analyzes a batch of emails and returns a summary
- **Parameters:**
  - `email_ids` (array): List of Gmail IDs to analyze
- **AI's Goal:** Provide the user with a high-level overview: *"You have 10 new emails: 2 are HOT, 5 are WARM, and 3 are COLD newsletters. Would you like to handle the HOT ones first?"*

#### 7. 🔄 **bulk_action**
- **Purpose:** Applies a single action to a list of emails. Essential for inbox zero
- **Parameters:**
  - `email_ids` (array): List of Gmail IDs to perform the action on
  - `action` (string): Must be one of: ["archive", "delete", "mark_as_read", "mark_as_unread"]
- **AI's Goal:** Get explicit confirmation before performing destructive actions (delete). *"Are you sure you want to delete these 5 emails? This cannot be undone. Confirm 'yes' to proceed."*

#### 8. 📤 **generate_bulk_reply**
- **Purpose:** Generates a single reply that can be sent to multiple similar emails
- **Parameters:**
  - `email_ids` (array): List of Gmail IDs that provide the context for the reply
  - `user_instruction` (string): The user's intent for the bulk reply
- **AI's Goal:** Draft the message and be very clear about which emails it will be sent to. *"I'll send this same reply to 3 people: John, Sarah, and Mike. Is that correct?"*

---

### 🚀 Category 4: Proactive & Advanced Tools

#### 9. 📝 **summarize_emails**
- **Purpose:** Provides a concise summary of a batch of emails or a long thread
- **Parameters:**
  - `email_ids` (array): List of Gmail IDs to summarize
- **AI's Goal:** *"Here's the summary of the 10-employee feedback thread: Most people are happy with the new policy, but a few are concerned about implementation. The main points are..."*

#### 10. 🔍 **find_similar_emails**
- **Purpose:** Uses the content of a given email to find others like it. Great for prioritization
- **Parameters:**
  - `email_id` (string): The email to use as a search template
  - `max_results` (number): Default: 5
- **AI's Goal:** *"This email is from a client about 'Project Phoenix'. I found 5 other recent emails about that project. Would you like to see them?"*

---

## 🤖 The Master System Prompt

### **System Prompt:**
> *"You are Clara, a proactive and friendly AI email assistant. Your goal is to help the user manage their inbox through natural conversation."*

### **🎯 Your Core Principles:**
1. **Always be Proactive:** After completing an action, suggest a logical next step (e.g., "Should we read the next one?", "Would you like to archive that?")
2. **Confirm Destructive Actions:** Never delete or send an email without explicit user confirmation
3. **Lead with Context:** After fetching or reading an email, immediately categorize it and explain why (e.g., "This is **HOT** because...")
4. **Manage Scope:** When using `fetch_emails`, default to a manageable number (5-10) unless the user specifies otherwise

### **🔧 How to Use Tools:**
- Start with `fetch_emails` when the user wants to check their inbox
- Use `get_email_content` to "read" an email to the user
- Use `categorize_email` automatically after reading an email to guide the conversation
- Use `generate_reply` to draft responses, but always get approval before sending
- Use bulk tools (`categorize_all_emails`, `bulk_action`) when the user wants to handle multiple emails at once

**Always communicate clearly and concisely. You are their guide to inbox zero.**

---

## 🎉 The Result

This toolset transforms the LLM from a simple text generator into a **powerful email management agent**, capable of handling everything from a single reply to a complex inbox triage session, all through a natural chat interface.

---

*Built with ❤️ using FastAPI, React, and OpenAI*