var context = []
var max_messages = 10;  // change this to adjust the number of messages to keep
var num_messages = 0;

function removeHASH() {
  if (window.location.href.indexOf('#') != -1)
    return window.location.href.substring(0, window.location.href.indexOf('#'));
  else {
    return window.location.href;
  }
}

function get_system_roles() {
  $.ajax({
    type: 'GET',
    url: 'get_system_roles',
    success: (data) => {
      console.log(data)
      data.forEach(element => {
        context.push(element)
      });
    }
  })
}

function restartRecording() {
   if (recorder && should_be_recording) { 
    console.log('restart recording called.')
    document.getElementsByClassName('micinvert')[0].style.backgroundColor = 'green';
    recorder.startRecording(); 
  } 
}

function sendGPT(msg) {
  var msgs = {};
  msgs.content = msg;
  msgs.role = 'user';
  context.push(msgs);

  // Update message count, ignoring 'system' role
  if (msgs.role !== 'system') num_messages++;

  $.ajax({
    type: 'POST',
    data: JSON.stringify(context),
    contentType: 'application/json',
    url: removeHASH() + 'chatgpt/send',
    success: (data) => {
      console.log(data);
      context = data
      manageMessage('ChatGPT', context.at(-1).content)

      if (robot != null) {
        robot.say(context.at(-1).content, restartRecording);
      } else {
        getTTS(context.at(-1).content, restartRecording);
      }
    }
  })
}

function getSTTNaoVer(wav) {
  data = {}
  data.filenameAudio = wav
  $.ajax({
      type: 'POST',
      url: 'watson/stt',
      data: JSON.stringify(data),
      contentType: false,
      processData: false,
      success: (data) => {
        console.log(data);
        if (data != '') {
          manageMessage('self', data);
          sendGPT(data);
        }
      }
  })
}

function getTTS(text, callback) {
  var chat_response = {};
  chat_response.text = text;
  chat_response.voice = 'en-US_AllisonVoice';
  console.log(text);
  $.ajax({
      type: 'POST',
      data: JSON.stringify(chat_response),
      contentType: 'application/json',
      url: removeHASH() + 'g/tts',
      success: (data) => {
        console.log(data)
        playFile(data, callback)
    }
  })
}

function getSTT(blob) {
  let fd = new FormData();
  fd.append('webm', blob);
  $.ajax({
    type: 'POST',
    url: 'trimAudio',
    data: fd,
    contentType: false,
    processData: false,
    success: (response) => { 
      console.log(response.message);
      $.ajax({
        type: 'POST',
        url: 'g/stt',
        data: JSON.stringify(response),
        contentType: 'application/json',
        processData: false,
        success: (data) => {
          console.log(data['transcript']);
          if (data['transcript']) {
            manageMessage('self', data['transcript']);
            sendGPT(data['transcript']);
          } else {
            restartRecording();
          }
        }
    })
    } 
  })
 
}

function importAudio() {
  data = {}
  data.filenameAudio = '/home/nao/recordings/microphones/audio.wav'
  data.endDirAudio = './public/raw_audio/';
  data.ip = robot.ip
  data.robotPass = 'nao'
  $.ajax({
    type: 'POST',
    data: JSON.stringify(data),
    contentType: 'application/json',
    url: removeHASH() + 'ssh/copy_recordings_audio',
    success: (data) => {
      console.log(data);
      getSTTNaoVer(data)
    }
  })
}

async function playFile(filename, callback) {
  var audio = new Audio(filename);  
  audio.type = 'audio/wav';

  audio.addEventListener('ended', () => {
    console.log('Audio playback finished');
    callback();
  })

  try {
    await audio.play();
    console.log('Playing...');
  } catch (err) {
    console.log('Failed to play...' + err);
  }
}