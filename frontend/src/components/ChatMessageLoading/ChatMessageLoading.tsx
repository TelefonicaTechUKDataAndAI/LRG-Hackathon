import { Card, Flex, Loader } from '@mantine/core';

export default function ChatMessageLoading() {
  return (
    <Flex justify="flex-start">
      <Card bg="gray.2" w="55%">
        <Loader color="blue" size="xs" />
      </Card>
    </Flex>
  );
}
