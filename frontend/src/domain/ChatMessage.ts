export default interface ChatMessage {
  message: string;
  role: 'bot' | 'person';
  type?: 'error' | null
}
