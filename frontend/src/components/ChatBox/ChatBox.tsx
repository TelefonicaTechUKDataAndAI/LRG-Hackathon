import { Button, Group, Stack, Textarea, Paper, Text, TextInput } from '@mantine/core';
import {
  IconClearAll,
  IconSend,
  IconTextScan2,
  IconLogs
} from '@tabler/icons-react';
import { useRef, useState } from 'react';

interface ChatBoxProps {
  textMessageCreated: (message: string) => void;
  chatHistoryCleared: () => void;
  selectedFiles: (files: File[] | null) => void;
  fetchPerson: (personId: number) => void;
  logChat: (personId: number) => void;
}

export default function ChatBox({
  textMessageCreated,
  chatHistoryCleared,
  selectedFiles,
  fetchPerson,
  logChat
}: ChatBoxProps) {
  const [message, setMessage] = useState<string>('');
  const [personId, setPersonId] = useState<string>('');

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
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', minWidth: 90 }}>
            <Text size="xs" fw={700} c="gray.7" mb={2}>
              Process
            </Text>
            <Paper withBorder radius="md" p="xs" style={{ borderColor: '#ccc', borderWidth: 1, borderStyle: 'solid', display: 'inline-block', textAlign: 'center' }}>
            <Group>
              <TextInput
                placeholder="Person ID"
                type="number"
                value={personId}
                onChange={(e) => setPersonId(e.currentTarget.value)}
              />
              <Button onClick={() => fetchPerson(parseInt(personId, 10))} leftSection={<IconTextScan2 />}>
                Search
              </Button>
              <Button onClick={() => logChat(parseInt(personId, 10))} leftSection={<IconLogs />}>
                Log Chat
              </Button>
              </Group>
            </Paper>
          </div>
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
