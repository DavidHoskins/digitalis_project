import { render, screen } from '@testing-library/react';
import App from './App';

test('Check app has loaded', () => {
  render(<App />);
  const linkElement = screen.getByTestId("App")
  expect(linkElement).toBeInTheDocument();
});
