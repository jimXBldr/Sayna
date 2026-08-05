# Test Case 1 

```
User: Tell Anu oluwapo that I will be back

Sayna:
Running Speech-To-Text...


==================================================
STT RESULT
==================================================
Transcript :  Tell Anu Luaqbautas I will be back.
Latency    : 5.931 seconds

Detecting Intent...

==================================================
INTENT RESULT
==================================================
Intent     : send_message
Parameters : {'chat': 'Anu Luaqbautas', 'message': 'I will be back.', 'query': None}
Latency    : 0.493 seconds

==================================================
PIPELINE SUMMARY
==================================================
STT Time      : 5.931 seconds
Intent Time   : 0.493 seconds
Total Time    : 6.424 seconds
```
---
# Test case 2;

```User; Go to Prince

Sayna;
Press Enter to start recording...

🎤 Recording...
Press Enter again to stop.


Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  Go to Chris
Latency    : 1.708 seconds

Detecting Intent...

==================================================
INTENT RESULT
==================================================
Intent     : open_chat
Parameters : {'chat': 'Chris', 'message': None, 'query': None}
Latency    : 1.064 seconds

==================================================
PIPELINE SUMMARY
==================================================
STT Time      : 1.708 seconds
Intent Time   : 1.064 seconds
Total Time    : 2.773 seconds
```
---
# Test Case 3:
```
User;  What time did David said we should meet?
Press Enter to start recording...

🎤 Recording...
Press Enter again to stop.



Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  What time did David said we should meet?
Latency    : 2.136 seconds

Detecting Intent...

==================================================
INTENT RESULT
==================================================
Intent     : extract_info
Parameters : {'chat': 'David', 'message': None, 'query': 'What time did David say we should meet?'}
Latency    : 0.730 seconds

==================================================
PIPELINE SUMMARY
==================================================
STT Time      : 2.136 seconds
Intent Time   : 0.730 seconds
Total Time    : 2.865 seconds
```
---
# Test Case 4;
```
User; 
Press Enter to start recording...

🎤 Recording...
Press Enter again to stop.



Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  I'm
Latency    : 2.102 seconds 

Detecting Intent...

Traceback (most recent call last):
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\main.py", line 165, in <module>
    main()
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\main.py", line 131, in main
    intent_result = intent_manager.detect_intent(
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\core\intent_manager.py", line 19, in detect_intent
    return self._build_intent_result(llm_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\core\intent_manager.py", line 43, in _build_intent_result
    parsed_response = self._validate_response(parse_response)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\core\intent_manager.py", line 27, in _validate_response
    raise InvalidIntentResponse('intent is not a string')
sayna_mvp_v1.support.exceptions.InvalidIntentResponse: intent is not a string
```
---
# TEST CASE 5;
```USER: Help me to check the address that Tolu sent.

Sayna
C:\Users\hp\PycharmProjects\learning_logR\.venv\Scripts\python.exe "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\main.py" 
Press Enter to start recording...

🎤 Recording...
Press Enter again to stop.



Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  Tudo do centro.
Latency    : 3.304 seconds

Detecting Intent...

==================================================
INTENT RESULT
==================================================
Intent     : open_chat
Parameters : {'chat': 'centro', 'message': None, 'query': None}
Latency    : 0.565 seconds

==================================================
PIPELINE SUMMARY
==================================================
STT Time      : 3.304 seconds
Intent Time   : 0.565 seconds
Total Time    : 3.869 seconds
```
---
# TEST CASE 6;
```
USER; Who is bringing the projector

SAYNA;
C:\Users\hp\PycharmProjects\learning_logR\.venv\Scripts\python.exe "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\main.py" 
Press Enter to start recording...

🎤 Recording...
Press Enter again to stop.



Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  Who is bringing the projector?
Latency    : 1.846 seconds

Detecting Intent...

==================================================
INTENT RESULT
==================================================
Intent     : extract_info
Parameters : {'chat': None, 'message': None, 'query': 'Who is bringing the projector?'}
Latency    : 0.655 seconds

==================================================
PIPELINE SUMMARY
==================================================
STT Time      : 1.846 seconds
Intent Time   : 0.655 seconds
Total Time    : 2.502 seconds

```
---
# TEST CASE 7;
```
User; I want to message James

Sayna;
Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  Alonso Messie James
Latency    : 1.641 seconds

Detecting Intent...

==================================================
INTENT RESULT
==================================================
Intent     : open_chat
Parameters : {'chat': 'Alonso Messie James', 'message': None, 'query': None}
Latency    : 0.692 seconds

==================================================
PIPELINE SUMMARY
==================================================
STT Time      : 1.641 seconds
Intent Time   : 0.692 seconds
Total Time    : 2.334 seconds
```
---
# Test case 8;
```
User; Summarize family group

Sayna;
Press Enter to start recording...

🎤 Recording...
Press Enter again to stop.



Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  Arise family group
Latency    : 1.877 seconds

Detecting Intent...

==================================================
INTENT RESULT
==================================================
Intent     : open_chat
Parameters : {'chat': 'family group', 'message': None, 'query': None}
Latency    : 0.733 seconds

==================================================
PIPELINE SUMMARY
==================================================
STT Time      : 1.877 seconds
Intent Time   : 0.733 seconds
Total Time    : 2.610 seconds
```
---

# Test Case 8;
```
User; Tell Subomi

Sayna;
Press Enter to start recording...

🎤 Recording...
Press Enter again to stop.



Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  Arise family group
Latency    : 1.877 seconds

Detecting Intent...

==================================================
INTENT RESULT
==================================================
Intent     : open_chat
Parameters : {'chat': 'family group', 'message': None, 'query': None}
Latency    : 0.733 seconds

==================================================
PIPELINE SUMMARY
==================================================
STT Time      : 1.877 seconds
Intent Time   : 0.733 seconds
Total Time    : 2.610 seconds
```
---
# Test Case 9
```
User; Open
Sayna;
C:\Users\hp\PycharmProjects\learning_logR\.venv\Scripts\python.exe "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\main.py" 
Press Enter to start recording...

🎤 Recording...
Press Enter again to stop.



Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  Open.
Latency    : 1.492 seconds

Detecting Intent...

==================================================
INTENT RESULT
==================================================
Intent     : open_chat
Parameters : {'chat': None, 'message': None, 'query': None}
Latency    : 0.492 seconds

==================================================
PIPELINE SUMMARY
==================================================
STT Time      : 1.492 seconds
Intent Time   : 0.492 seconds
Total Time    : 1.984 seconds
```
---
# Test Case; 10

```
User; Play music
Sayna;
Press Enter to start recording...

🎤 Recording...
Press Enter again to stop.



Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  Lý mjúzík
Latency    : 3.298 seconds

Detecting Intent...

Traceback (most recent call last):
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\main.py", line 165, in <module>
    main()
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\main.py", line 131, in main
    intent_result = intent_manager.detect_intent(
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\core\intent_manager.py", line 19, in detect_intent
    return self._build_intent_result(llm_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\core\intent_manager.py", line 43, in _build_intent_result
    parsed_response = self._validate_response(parse_response)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\core\intent_manager.py", line 27, in _validate_response
    raise InvalidIntentResponse('intent is not a string')
sayna_mvp_v1.support.exceptions.InvalidIntentResponse: intent is not a string
```
# Test Case  11
```User; Do that thing
Sayna;
Press Enter to start recording...

🎤 Recording...
Press Enter again to stop.



Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  Dúdart þín.
Latency    : 2.296 seconds

Detecting Intent...

Traceback (most recent call last):
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\main.py", line 165, in <module>
    main()
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\main.py", line 131, in main
    intent_result = intent_manager.detect_intent(
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\core\intent_manager.py", line 19, in detect_intent
    return self._build_intent_result(llm_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\core\intent_manager.py", line 43, in _build_intent_result
    parsed_response = self._validate_response(parse_response)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\core\intent_manager.py", line 27, in _validate_response
    raise InvalidIntentResponse('intent is not a string')
sayna_mvp_v1.support.exceptions.InvalidIntentResponse: intent is not a string
```

# Test Case; 12
```
User; Can you quickly tell Mr James that I will be there in 5 minutes

Sayna;
C:\Users\hp\PycharmProjects\learning_logR\.venv\Scripts\python.exe "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\main.py" 
Press Enter to start recording...

🎤 Recording...
Press Enter again to stop.



Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  Can you quickly tell Mr. James that I'll be there in five minutes?
Latency    : 2.925 seconds

Detecting Intent...

==================================================
INTENT RESULT
==================================================
Intent     : send_message
Parameters : {'chat': 'Mr. James', 'message': "I'll be there in five minutes", 'query': None}
Latency    : 0.720 seconds

==================================================
PIPELINE SUMMARY
==================================================
STT Time      : 2.925 seconds
Intent Time   : 0.720 seconds
Total Time    : 3.645 seconds
```
---
# Test Case 13
```
User; Can you please tell me what everyone has been saying on the engineering group while I was asleep?
Sayna;
Press Enter to start recording...

🎤 Recording...
Press Enter again to stop.



Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  Can you please tell me what everyone has been saying on the engineering group while I was asleep?
Latency    : 1.973 seconds

Detecting Intent...

==================================================
INTENT RESULT
==================================================
Intent     : summarize_chat
Parameters : {'chat': 'engineering group', 'message': None, 'query': None}
Latency    : 0.644 seconds

==================================================
PIPELINE SUMMARY
==================================================
STT Time      : 1.973 seconds
Intent Time   : 0.644 seconds
Total Time    : 2.617 seconds
```

# Test case 14; 
```
User; Abeg tell Abimbola that I will soon reach, tell Mr Abimbola that I will soon be there.
Sayna;


Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  A wè ddiw abinbola dat awsun bide, daun nista abinbola dat awsun bide
Latency    : 2.826 seconds

Detecting Intent...

Traceback (most recent call last):
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\main.py", line 165, in <module>
    main()
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\main.py", line 131, in main
    intent_result = intent_manager.detect_intent(
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\core\intent_manager.py", line 19, in detect_intent
    return self._build_intent_result(llm_response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\core\intent_manager.py", line 43, in _build_intent_result
    parsed_response = self._validate_response(parse_response)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\core\intent_manager.py", line 27, in _validate_response
    raise InvalidIntentResponse('intent is not a string')
sayna_mvp_v1.support.exceptions.InvalidIntentResponse: intent is not a string
```
# Test case 15
```mermaid
User; please now open the family group

Sayna;
Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  Please now open the family group.
Latency    : 1.964 seconds

Detecting Intent...

==================================================
INTENT RESULT
==================================================
Intent     : open_chat
Parameters : {'chat': 'family group', 'message': None, 'query': None}
Latency    : 0.519 seconds

==================================================
PIPELINE SUMMARY
==================================================
STT Time      : 1.964 seconds
Intent Time   : 0.519 seconds
Total Time    : 2.483 seconds

```
# Test case 16
```
User; Oya send I am outside to Tobi.
Sayna;
🎤 Recording...
Press Enter again to stop.



Running Speech-To-Text...

==================================================
STT RESULT
==================================================
Transcript :  Og ja, senda máltsætt til því.
Latency    : 1.743 seconds

Detecting Intent...

==================================================
INTENT RESULT
==================================================
Intent     : send_message
Parameters : {'chat': None, 'message': 'máltsætt', 'query': None}
Latency    : 0.655 seconds

==================================================
PIPELINE SUMMARY
==================================================
STT Time      : 1.743 seconds
Intent Time   : 0.655 seconds
Total Time    : 2.398 seconds
```