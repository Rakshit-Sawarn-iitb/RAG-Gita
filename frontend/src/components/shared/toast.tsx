import * as Sentry from '@sentry/react';
import { message } from 'antd';

type ToastParams = {
  content?: string | { message: string }; // The type of content can be a string or an object
  status: 'success' | 'error' | 'info' | 'warning' | 'loading'; // Status for message
  key?: string; // Optional key for message
};

const toast = ({ content = 'Loading...', status, key }: ToastParams): void => {
  message.destroy(); // Clears all messages before displaying the new one

  // If content is an object with a "message" property, extract the message
  if (typeof content === 'object' && 'message' in content) {
    message[status]({ content: content.message, key });
    Sentry.captureException(content.message); // Log to Sentry
  } else {
    // Handle simple string content
    message[status]({ content, key });
  }
};

export default toast;
