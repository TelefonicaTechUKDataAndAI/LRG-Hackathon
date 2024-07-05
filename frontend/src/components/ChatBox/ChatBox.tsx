import { Button, FileInput, Group, Stack, Textarea } from '@mantine/core';
import { useRef, useState } from 'react';

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
  const handleAudioFileClick = () => {
    if (hiddenFileInput.current) {
      hiddenFileInput.current.click();
    }
  };

  const handleNewTextMessage = () => {
    textMessageCreated(message);
    setMessage('');
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
            <Button onClick={handleNewTextMessage}>Send</Button>
            <Button onClick={handleAudioFileClick}>Upload Audio</Button>
            <Button>Record Audio</Button>
          </Group>
          <Group ml="auto">
            <Button variant="outline" onClick={chatHistoryCleared}>
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
