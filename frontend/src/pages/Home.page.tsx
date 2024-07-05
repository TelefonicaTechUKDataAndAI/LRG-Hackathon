import { useState } from 'react';
import { Box, Container, Stack } from '@mantine/core';
import ChatMessage from '@/domain/ChatMessage';
import ChatBox from '@/components/ChatBox/ChatBox';
import ChatWindow from '@/components/ChatWindow/ChatWindow';

export function HomePage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const textMessageCreated = (message: string) => {
    setMessages((oldMessages) => [...oldMessages, { message, role: 'person' }]);

    setLoading(true);

    fetch('/api/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ body: message }),
    })
      .then((response) => response.json())
      .then((data) => {
        setMessages((oldMessages) => [...oldMessages, { message: data.response, role: 'bot' }]);
        setLoading(false);
      })
      .catch((error) => {
        setMessages((oldMessages) => [
          ...oldMessages,
          { message: 'Error: '.concat(error), role: 'bot' },
        ]);
        setLoading(false);
      });
  };

  const audioFileUploaded = (file: File | null) => {
    setMessages((oldMessages) => [
      ...oldMessages,
      { message: '🎵 Audio Uploaded...', role: 'person' },
    ]);

    setLoading(true);

    fetch('/api/process-audio-file', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/octet-stream',
      },
      body: file,
    })
      .then((response) => response.json())
      .then((data) => {
        setMessages((oldMessages) => [...oldMessages, { message: data.response, role: 'bot' }]);
        setLoading(false);
      })
      .catch((error) => {
        setMessages((oldMessages) => [
          ...oldMessages,
          { message: 'Error: '.concat(error), role: 'bot' },
        ]);
        setLoading(false);
      });
  };

  const clearChatHistory = () => setMessages([]);

  return (
    <Container fluid>
      <Stack style={{ height: '87vh' }} p={0}>
        <ChatWindow messages={messages} loading={loading} />
        <Box>
          <ChatBox
            textMessageCreated={textMessageCreated}
            chatHistoryCleared={clearChatHistory}
            audioFileUploaded={audioFileUploaded}
          />
        </Box>
      </Stack>
    </Container>
  );
}
