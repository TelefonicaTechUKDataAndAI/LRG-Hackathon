import { Button, FileInput, Group, Stack, Textarea } from '@mantine/core';
import {
  IconClearAll,
  IconMicrophone,
  IconMicrophoneOff,
  IconSend,
  IconUpload,
} from '@tabler/icons-react';
import { useRef, useState } from 'react';
import { useReactMediaRecorder } from 'react-media-recorder-2';

interface ChatBoxProps {
  textMessageCreated: (message: string) => void;
  chatHistoryCleared: () => void;
  audioFileUploaded: (file: File | null) => void;
}

export default function ChatBox({
  textMessageCreated,
  chatHistoryCleared,
  audioFileUploaded,
}: ChatBoxProps) {
  const [message, setMessage] = useState<string>('');

  const hiddenFileInput = useRef<HTMLButtonElement>(null);
  const onAudioFileClick = () => {
    if (hiddenFileInput.current) {
      hiddenFileInput.current.click();
    }
  };

  const onNewTextMessage = () => {
    textMessageCreated(message);
    setMessage('');
  };

  const onRecordingComplete = (blobUrl: string, blob: Blob) => {
    const file = new File([blob], 'audio.wav', {
      type: blob.type,
    });

    console.log(blob);

    audioFileUploaded(file);
  };

  const { status, startRecording, stopRecording } = useReactMediaRecorder({
    audio: true,
    blobPropertyBag: {
      type: 'audio/webm',
    },
    onStop: onRecordingComplete,
  });

  const isRecording = () => status === 'recording';

  const onRecordingClick = () => {
    if (isRecording()) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <>
      <Stack>
        <Textarea
          placeholder="Type your message here"
          autosize
          minRows={7}
          value={message}
          onChange={(e) => setMessage(e.currentTarget.value)}
        />
        <Group w="100%">
          <Group>
            <Button onClick={onNewTextMessage} leftSection={<IconSend />}>
              Send
            </Button>
            <Button onClick={onAudioFileClick} leftSection={<IconUpload />}>
              Upload Audio
            </Button>
            <Button
              leftSection={isRecording() ? <IconMicrophone /> : <IconMicrophoneOff />}
              onClick={onRecordingClick}
            >
              {isRecording()
                ? // ? 'Stop Recording" ('.concat(recorderControls.recordingTime.toString(), ')')
                  'Stop Recording'
                : 'Start Recording'}
            </Button>
          </Group>
          <Group ml="auto">
            <Button variant="outline" onClick={chatHistoryCleared} leftSection={<IconClearAll />}>
              Clear Chat
            </Button>
          </Group>
        </Group>
        <FileInput
          label="Audio File"
          description="Audio File"
          placeholder="Audio File"
          style={{ display: 'none' }}
          onChange={audioFileUploaded}
          ref={hiddenFileInput}
        />
      </Stack>
    </>
  );
}
