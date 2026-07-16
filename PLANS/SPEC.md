# Technical Specification

# Phase 1: Product Definition
## 1. Problem Statement:
People currently interact with software by translating their intentions into sequences of manual actions such, 
as navigating interfaces, clicking, scrolling, and typing. These interactions are often slower than expressing 
the intention directly and require unnecessary cognitive effort. This friction is especially noticeable in communication
platforms like WhatsApp, where users repeatedly perform tasks such as sending messages, locating conversations, 
and extracting important information from long chat histories. As conversations grow, important information can become 
buried under large volumes of messages, increasing the effort required to find and act on relevant information.

---
# 2. Goals 
## 2.1 User Goal
Enable user to express their intentions naturally with minimal cognitive effort, allowing common whatsapp task to 
be completed without manually navigating interfaces.

## 2.2 Business Goal                                                  
Validate whether users prefer expressing common whatsapp task through speech instead of manually interacting 
with interface.


## 2.3 Engineering Goal
Demonstrate that spoken english can be reliably converted into user intentions and executed as correct actions in 
whatsapp web using automation.

## 2.4 MVP Validation
Determine whether sayna can consistently interpret spoken user intentions and execute the intended user whatsapp 
action accurately enough for users to trust it for everyday use.
---

## Architectural decision

Every architectural decision must either strengthen or simplify the experiment of determining whether people prefer 
to express common whatsapp task through speech rather than manual interaction 
---

# 3. Non Goals
- No other apps just whatsapp
- No other lang just english
- Not a conversational AI assistant
- Not built for scale
- Not every desktop application
- Not other platforms like ios, android just web
- No chat interface

---

# 4. User Personas

## 4.1 Primary Personas
Individuals who rely on WhatsApp as a primary communication channel for time-sensitive or important information and 
perform repetitive tasks such as sending messages, locating conversations, extracting information, or reviewing long 
chat histories. These users experience friction from repeatedly navigating interfaces to accomplish routine tasks.


## 4.2 Behaviors
- Frequently communicates through WhatsApp.
- Depends on WhatsApp for information that requires timely action.
- Performs repetitive interactions.
- Navigates long conversations to locate relevant information.
- Wants to complete tasks with minimal cognitive effort.

## 4.3 Negative Personas
- Rarely use WhatsApp.
- Perform very few WhatsApp tasks.
- Do not rely on WhatsApp for important communication.
- Need broad desktop automation beyond WhatsApp.
- Are evaluating Sayna primarily as a conversational AI rather than as a voice-first task execution tool.

---

# 5. Functional Requirements.

## 5.1 Core Functional Requirements.
1. The system shall accept spoken english commands from the user
2. The system shall provide clear feedback when it is actively listening to the user input
3. The system shall interpret supported user requests and execute the corresponding whatsapp action
4. The system shall notify the user when an action has been done completely
5. The system shall notify the user when an action fails and where possible and explain the reason

## 5.2 Error and Recovery Requirements
1. If spoken input could not be understood the system shall inform the user and allow them to try again.
2. If the spoken language is not supported the system shall inform the user that only english is supported.
3. If the user's request is outside the supported capabilities of the MVP, the system shall inform the user that the request is unsupported.
4. If the user's intent cannot be determined, the system shall explain that it could not understand the request.
5. If the requested WhatsApp resource (such as a chat) cannot be found, the system shall notify the user.
6. If multiple possible matches exist, the system shall request clarification before executing any action.
7. If WhatsApp Web is unavailable or inaccessible, the system shall notify the user.

## 5.3 Execution Requirements.
1. The system shall process one command at a time.
2. The system shall not resolve ambiguous statements without first resolving the ambiguity.

---

# 6. Non Functional Requirements

## 6.1 Responsiveness
1. The system should provide immediate feedback when listening for user input.
2. Supported tasks should complete within a duration that feels responsive for interactive use, with approximately 5 seconds as the target for the MVP under normal conditions.

## 6.2 Reliability
1. The system should execute supported actions consistently enough that users can rely on it for everyday WhatsApp tasks.
2. When confidence in the user's intent is insufficient, the system should request clarification instead of guessing.

## 6.3 Usability 
1. The interaction should minimize the mental effort required to complete common whatsapp tasks
2. Users should be able to express intentions naturally without learning rigid commands

## 6.3 Error Communication
1. The system should clearly explain failures whenever possible.
2. Users should receive enough information to decide what the next step is rather than the system attempting complex automatic recovery.

## 6.4 Simplicity
1. The MVP should optimize for correctness and user trust over maximizing automations
2. The system should refuse ambiguous request until further clarifications have been provided

---

# 7. Constraints
1. The execution surface is whatsapp web
2. Voice-Only Interaction
3. English Only
4. Immediate Execution
---

# 8. Assumptions
1. We believe that expressing intentions through speech reduces cognitive effort.
2. The friction in whatsapp is significant enough that people are willing to change their behavior to remove it.
3. Users are comfortable speaking to software for productivity tasks.
4. Users naturally express their intentions in ways that can be interpreted reliably.
5. WhatsApp Web exposes enough UI consistency for browser automation to remain reliable.
6. The supported tasks (send message, summarize chat, extract information, open chat) represent meaningful pain points for users.

---

# 9. User Flows
```mermaid
User
↓

Speak

↓

Understand

↓

Clarify

↓

Execute

↓

Respond
```
## 9.1 User flow: Extract information
``` mermaid
User opens Sayna
        ↓
Sayna indicates it is ready and begins listening
        ↓
User speaks a request
        ↓
Sayna acknowledges that it received the request
        ↓
Sayna determines whether the request can be safely executed
        ↓
        ├── Yes
        │      ↓
        │  Process the request
        │      ↓
        │  Retrieve the requested information from WhatsApp
        │      ↓
        │  Present the result to the user
        │      ↓
        │  End interaction
        │
        └── No
               ↓
        Ask for the missing information
               ↓
        User provides clarification
               ↓
        Continue processing the original request
               ↓
        Retrieve the requested information
               ↓
        Present the result
               ↓
        End interaction
```
## 9.2 Failure Paths
Unsupported request
```mermaid
User speaks
      ↓
Request is outside MVP capabilities
      ↓
Sayna explains that the request is not supported
      ↓
End interaction
```
Speech not understood
```mermaid
User speaks
      ↓
Speech cannot be understood
      ↓
Sayna asks the user to try again
      ↓
Return to listening
```
Unsupported language
```mermaid
User speaks in a language other than English
      ↓
Sayna explains that only English is supported
      ↓
Return to listening
```
Whatsapp unavailable
```mermaid
User requests an action
      ↓
WhatsApp Web is unavailable
      ↓
Sayna explains the problem
      ↓
End interaction
```
Action fails
```mermaid
User request is understood
      ↓
Execution begins
      ↓
Execution fails
      ↓
Sayna explains why the action failed
      ↓
End interaction
```
---

# 10. High Level architecture
```mermaid
                    ┌────────────────────────────┐
                    │     Presentation Layer     │
                    │           (UI)             │
                    └─────────────┬──────────────┘
                                  │
                                  │ User events
                                  ▼
                    ┌───────────────────────────┐
                    │    Request Coordinator    │
                    │                           │
                    │ Owns:                     │
                    │ • Request lifecycle       │
                    │ • Execution context       │
                    │ • Application state       │
                    └──────┬──────────┬─────────┘
                           │          │
           ┌───────────────┘          └───────────────┐
           ▼                                          ▼
 ┌─────────────────┐                      ┌──────────────────┐
 │  Voice Manager  │                      │  Intent Manager  │
 └─────────────────┘                      └────────┬─────────┘
                                                   │
                                                   ▼
                                      ┌────────────────────────┐
                                      │ Clarification Manager  │
                                      └───────────┬────────────┘
                                                  │
                                                  ▼
                                     ┌─────────────────────────┐
                                     │ WhatsApp Action Manager │
                                     └─────────────────────────┘
                                                  │
                                                  │
                                                  ▼
                                     ┌─────────────────────────┐
                                     │   Content Processor     │
                                     └─────────────────────────┘
```
---
# 11. Components Responsibilities

## 11.1 Request Coordinator
### Purpose 
Owns the life cycle of a user request from start to finish

### Responsibilities
- Receive new requests from the UI
- Maintain the temporary execution context
- Invoke the appropriate components at each stage
- Interpret components results
- Decide how the workflow proceeds
- Pause and resume execution after clarification
- Notify the UI of application state changes

### Must Not
- Understand user intent.
- Perform speech recognition.
- Execute WhatsApp operations.
- Render the UI.
- Parse WhatsApp messages.
- Use Playwright directly.

### Owns 
- Current request context
- Workflow state.
- Application State

### Receives
- User requests from the UI
- Results from all other components

### Returns
- Application state updates and user-facing outcomes to the Presentation Layer.

## 11.2 Intent manager
### Purpose 
Translate natural language into a structured request that the rest of the system can execute.

### Responsibilities
- Receive transcript
- Identify the users intent
- Extract the required parameters
- Produce a structured request
- Reports success or failure with reason for failure

### Must Not
- Execute WhatsApp actions.
- Ask clarification questions.
- Coordinate workflow.
- Render UI.
- Maintain request state.
- Retry requests.

### Input
Transcript - plain english

### Output
- Success
- Structured Request
- Failure Reason
---

#### Structured Request
The canonical representation of what the user wants to accomplish after natural language has been understood

##### Purpose
Represent the users intent in a structured implementation-independent format after natural language has been understood.

##### Fields
```mermaid
Structured Request
-----------------
Intent

Parameters
```

### Examples

##### 1. Send Message
```mermaid
Intent; send message
Parameters
---------
chat

message
```

##### 2. Summarize Chats
```mermaid
intent; summarize chat
parameters;
    chat
```
##### 3. extract info
```mermaid
intent; extract_info
parameters;
    chat
    query
```
---

## 11.3 Voice Manager 

### Purpose
Isolate all voice processing concerns from the rest of the components

### Responsibilities
- Produce a transcript
- Return transcription result
- Report voice processing failures
- Receive audio

### Not to do
- Understand intent
- parse user request
- validate missing parameters
- execute whatsappp actions
- manage workflow
- store request state
- render the UI
- decides what happens next after transcription

### Input
- audio

### Output
```mermaid
VoiceResult
-----------
success
transcript
failure and reason
```

## 11.4 Whatsapp Action Manager

#### Purpose
It isolates all interactions with WhatsApp Web from the rest of the application.

### Responsibilities
Search chat, open chat, read messages, send messages, retrieve relevant messages

### Not to do
- extract info
- summarize messages
- detect intent

### Input
Structured Request

### Output
```mermaid
ActionResult
------------
success

data(optional)

failureReason
```
## 11.5 Content Processor

### Purpose 
To  process the received whatsapp content into the information requested by the user.

### Responsibilities
- receives the content and intent
- produces summarized content
- returns the processing result
- process content according to intent(extract content and summarize content)
- Report when processing cannot be completed because the request is too vague or the content doesn't contain the requested information.

### Not to 
- detect intent
- perform any whatsapp web automation task
- resolve ambiguity or missing information 
- perform any unrelated task that doesn't involve summarization or extraction.

### Input
Content Processing Request - intent, content, parameters

### Output
```mermaid
ProcessedResult
--------------
success

processed content

MissingInformation(optional)

failureReason
```

## 11.6 Clarification Manager

### Purpose
To translate system uncertainty into clear questions that the user can answer and to interpret the users responses
### Responsibilities
- Receives a request for clarification.
- Determines what question to ask.
- Interprets the user's clarification response.
- Returns updated parameter values.
- Generate user-friendly clarification prompts

### It does not:
- Search WhatsApp.
- Detect multiple chats.
- Decide whether a query is vague.
- Own the Current Request.

### Input
ClarificationRequest - failure reason, missing information, candidates(optional), currentparameters

### Output
Clarification Prompt - success Questions and Options(optional) failureReason
Clarification Result - success updated parameters failureReason

## 11.7 Presentation Manager

### Purpose
To manage all interactions between the user and the application while keeping the application independent of the user
interface

### Responsibilities
- Display the application.
- receive audio from microphone
- Stop and start audio
- Display the current execution state
    Examples:
        Listening...
        Understanding...
        Executing...
        Waiting for clarification...
        Completed...
        Failed...
- Send captured audio to the request coordinator
- Display result
- Capture clarification answers

### Must not do
- Detect intent.
- Parse transcripts.
- Decide which WhatsApp action to execute.
- Call Playwright.
- Search WhatsApp.
- Summarize conversations.
- Update the Current Request.
- Coordinate the workflow.

### Input
The Presentation Layer receives events from the user and display instructions from the Request Coordinator.

User events include:
Microphone pressed
Audio captured
Clarification answer submitted

Coordinator instructions include:
Show listening
Show processing
Show clarification
Show success
Show failure
Display summary
Display extracted information

### Output
```mermaid
Presentation Event
------------------
Success

AudioCaptured

Clarification Response

RetryRequested

FailureReason
```

## 12. Folder Structure
