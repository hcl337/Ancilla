import subprocess, os, time, signal

command = "pocketsphinx_continuous -hmm /usr/local/share/pocketsphinx/model/en-us/en-us -lm /Users/hcl337/Documents/code/ancilla/Ancilla/src/hearing/sphinx_vocabulary/vocab.lm -dict /Users/hcl337/Documents/code/ancilla/Ancilla/src/hearing/sphinx_vocabulary/vocab.dic -samprate 16000/8000/4000 -inmic yes"
command = command.split()

#hearingProcess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
hearingProcess = subprocess.Popen(command, stdout=subprocess.PIPE, preexec_fn=os.setsid)

time.sleep(10)
startTime = time.time()

while hearingProcess.poll() is None:

    print("Waiting for line")
    # This waits for each line to come in
    phrase = hearingProcess.stdout.readline() # This blocks until it receives a newline.
    print(">>> " + phrase)

    if time.time() - startTime > 10:    
        print("10 seconds are up")
        break


os.killpg(os.getpgid(hearingProcess.pid), signal.SIGTERM)
