import { useState } from 'react';
import { Box, Container, Stack } from '@mantine/core';
import ChatMessage from '@/domain/ChatMessage';
import ChatBox from '@/components/ChatBox/ChatBox';
import ChatWindow from '@/components/ChatWindow/ChatWindow';

export function HomePage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const handleError = async (error: Response) => {
    console.log(error);

    const contentType = error.headers.get('content-type');
    let errorDetail = 'Unknown Error - Status Code '.concat(error.status.toString());

    if (contentType && contentType.indexOf('application/json') !== -1) {
      errorDetail = (await error.json()).detail;
    }

    setMessages((oldMessages) => [
      ...oldMessages,
      { message: 'Error: '.concat(errorDetail), role: 'bot', type: 'error' },
    ]);
    setLoading(false);
  };

  const sendChatRequest = (endpoint: string, headers: any, body: any) => {
    fetch(endpoint, {
      method: 'POST',
      headers,
      body,
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        return Promise.reject(response);
      })
      .then((data) => {
        setMessages((oldMessages) => [...oldMessages, { message: data.response, role: 'bot' }]);
        setLoading(false);
      })
      .catch(async (error) => handleError(error));
  };

  const textMessageCreated = (message: string) => {
    setMessages((oldMessages) => [...oldMessages, { message, role: 'person' }]);
    setLoading(true);

    sendChatRequest(
      '/api/process',
      {
        'Content-Type': 'application/json',
      },
      JSON.stringify({ body: message })
    );
  };

  const audioFileUploaded = (file: File | null) => {
    setMessages((oldMessages) => [
      ...oldMessages,
      { message: '🎵 Audio Uploaded...', role: 'person' },
    ]);

    setLoading(true);

    const formData = new FormData();
    formData.append('request', file);

    sendChatRequest('/api/process-audio-file', {}, formData);
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
