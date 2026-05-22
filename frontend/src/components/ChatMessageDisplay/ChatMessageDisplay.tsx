import { Card, Flex } from '@mantine/core';
import ReactMarkdown from 'react-markdown';
import ChatMessage from '@/domain/ChatMessage';

interface ChatMessageDisplayProps {
  message: ChatMessage;
}

export default function ChatMessageDisplay({ message }: ChatMessageDisplayProps) {
  const justify = message.role === 'bot' ? 'flex-start' : 'flex-end';
  let bg = message.role === 'bot' ? 'gray.2' : 'green.4';

  if (message.type === 'error') {
    bg = 'red.4';
  }

  return (
    <Flex justify={justify}>
      <Card bg={bg} w="55%" shadow="none">
        <ReactMarkdown skipHtml>{message.message}</ReactMarkdown>
      </Card>
    </Flex>
  );
}
