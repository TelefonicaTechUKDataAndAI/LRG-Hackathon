import { Button, Group, Stack, Textarea, Paper, Text } from '@mantine/core';
import {
  IconClearAll,
  IconSend,
  IconUpload,
  IconTextScan2
} from '@tabler/icons-react';
import { useRef, useState } from 'react';
import { useReactMediaRecorder } from 'react-media-recorder-2';

interface ChatBoxProps {
  textMessageCreated: (message: string) => void;
  chatHistoryCleared: () => void;
  selectedFiles: (files: File[] | null) => void;
  redactText: () => void;
}

export default function ChatBox({
  textMessageCreated,
  chatHistoryCleared,
  selectedFiles,
  redactText
}: ChatBoxProps) {
  const [message, setMessage] = useState<string>('');

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      onNewTextMessage();
    }
  };
  
  const onNewTextMessage = () => {
    textMessageCreated(message);
    setMessage('');
  };

  const hiddenFileInput = useRef<HTMLInputElement>(null);

  const onFolderSelection = () => {
    if (hiddenFileInput.current) {
      hiddenFileInput.current.value = '';
      hiddenFileInput.current.click();
    }
  };

  // Handle file/folder selection
  const onFilesSelected = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      // Convert FileList to Array
      const fileArray = Array.from(files)
      selectedFiles(fileArray);
    } else {
      selectedFiles(null);
    }
  };

  return (
    <Paper withBorder radius="md" p="md" style={{ position: 'relative', borderColor: '#ccc', borderWidth: 1, borderStyle: 'solid' }}>
      <Stack>
        <Textarea
          placeholder="Type your message here"
          autosize
          minRows={7}
          value={message}
          onChange={(e) => setMessage(e.currentTarget.value)}
          onKeyDown={handleKeyDown}
        />
        <Group w="100%">
          {/* <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', minWidth: 90 }}>
            <Text size="xs" fw={700} c="gray.7" mb={2}>
              Process
            </Text>
            <Paper withBorder radius="md" p="xs" style={{ borderColor: '#ccc', borderWidth: 1, borderStyle: 'solid', display: 'inline-block', textAlign: 'center' }}>
            <Group>
              <Button onClick={onFolderSelection} leftSection={<IconUpload />}>
                Select folder
              </Button>
              <Button onClick={redactText} leftSection={<IconTextScan2 />}>
                Redact Text
              </Button>
              </Group>
            </Paper>
          </div> */}
          <Group ml="auto">
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', minWidth: 90 }}>
            <Text size="xs" fw={700} c="gray.7" mb={2}>
              Chat
            </Text>
            <Paper withBorder radius="md" p="xs" style={{ borderColor: '#ccc', borderWidth: 1, borderStyle: 'solid', display: 'inline-block', textAlign: 'center' }}>
              <Group>
              <Button onClick={onNewTextMessage} leftSection={<IconSend />}>
                Send
              </Button>
              <Button variant="outline" onClick={chatHistoryCleared} leftSection={<IconClearAll />}>
              Clear Chat
            </Button>
            </Group>
            </Paper>
            </div>
        </Group>
        </Group>
        {/* Hidden native file input for folder/file selection */}
        <input
          type="file"
          style={{ display: 'none' }}
          ref={hiddenFileInput}
          onChange={onFilesSelected}
          multiple
          // @ts-ignore
          webkitdirectory="true"
        />
      </Stack>
    </Paper>
  );
}
