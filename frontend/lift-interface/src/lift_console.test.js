import { render, screen } from '@testing-library/react';
import LiftConsole from './lift_console';
import { act , waitFor} from "react-dom/test-utils";
import userEvent from "@testing-library/user-event";

test('Check lift console has loaded', async () => {
    const mockedLiftConfig = {"lifts": [{"serviced_floors": [0, 1, 2]}, {"serviced_floors": [0, 1, 2, 3, 4]}, {"serviced_floors": [4, 5, 6]}]};
    jest.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({json: () => Promise.resolve(mockedLiftConfig)}));

    await act(async () => {
        render(<LiftConsole current_floor={0}/>);
      });
    
    const linkElement = screen.getByTestId("LiftConsole");
    expect(linkElement).toBeInTheDocument();

    const elements = await screen.findAllByTestId("LiftConsoleButton");
    expect(elements.length).toBe(5);
});

test('Check lift console can make requests', async () => {
    const mockedLiftConfig = {"lifts": [{"serviced_floors": [0, 1, 2]}, {"serviced_floors": [0, 1, 2, 3, 4]}, {"serviced_floors": [4, 5, 6]}]};
    jest.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({json: () => Promise.resolve(mockedLiftConfig)}));

    await act(async () => {
        render(<LiftConsole current_floor={0}/>);
      });

    const elements = await screen.findAllByTestId("LiftConsoleButton");
    expect(elements.length).toBe(5);

    const mockedLiftRequest = {"lift": 0};
    const mockCallback = jest.fn(() => Promise.resolve(mockedLiftRequest));

    jest.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({json: mockCallback}));
    await act(async () => {
        userEvent.click(elements[1]);
    });
    expect(mockCallback.mock.calls).toHaveLength(1);

});

test('Check lift console can request status', async () => {
    const mockedLiftConfig = {"lifts": [{"serviced_floors": [0, 1, 2]}, {"serviced_floors": [0, 1, 2, 3, 4]}, {"serviced_floors": [4, 5, 6]}]};
    jest.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({json: () => Promise.resolve(mockedLiftConfig)}));

    await act(async () => {
        render(<LiftConsole current_floor={0}/>);
      });

    const elements = await screen.findAllByTestId("LiftConsoleButton");

    const mockedLiftRequest = {"lift": 0};
    const mockCallback = jest.fn(() => Promise.resolve(mockedLiftRequest));

    jest.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({json: mockCallback}));
    await act(async () => {
        userEvent.click(elements[1]);
    });

    const mockedLiftStatus = {"lifts" : [{"floor": 0, "destinations": [1,5,10]}, {"floor": 0, "destinations": [1,10]}]};
    const mockCallbackStatus = jest.fn(() => Promise.resolve(mockedLiftRequest));

    jest.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({json: mockCallbackStatus}));
    await act(async () => {
        userEvent.click(elements[1]);
    });
    expect(mockCallback.mock.calls).toHaveLength(1);
});