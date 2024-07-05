import { ScrollArea, Stack } from '@mantine/core';
import ChatMessage from '@/domain/ChatMessage';
import ChatMessageDisplay from '../ChatMessageDisplay/ChatMessageDisplay';
import ChatMessageLoading from '../ChatMessageLoading/ChatMessageLoading';

interface ChatWindowProps {
  messages: ChatMessage[];
  loading: boolean;
}

export default function ChatWindow({ messages, loading }: ChatWindowProps) {
  return (
    <ScrollArea p="xs" scrollbarSize={12} style={{ height: '75vh' }}>
      <Stack>
        {messages.map((message, index) => (
          <ChatMessageDisplay key={index} message={message} />
        ))}
        {loading && <ChatMessageLoading />}
      </Stack>
    </ScrollArea>
  );
}
