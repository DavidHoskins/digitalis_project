import React from 'react';

import { useState, useEffect } from 'react';

import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';

class LiftConsole extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            data: [],
            elevator_choice: []
        };
    }

    get_lift_status = async (intervalId) => { 
        try {
            await fetch('http://127.0.0.1:8000/api/lift/status/')
            .then((res) => {
                return res.json();
            }).catch((error) => {
                console.log(error);
            })
            .then((data) => {
                for(let i = 0; i < data["lifts"].length; i++)
                {
                    if(this.state.elevator_choice.includes(i))
                    {
                        if(data["lifts"][i]["floor"] == this.props.current_floor || !data["lifts"][i]["destinations"].includes(i))
                        {
                            const removed_list = this.state.elevator_choice.filter((elevator_number) => elevator_number != i);
                            this.setState({elevator_choice : removed_list});
                            clearInterval(intervalId);
                        }
                    }
                }
            }).catch((error) => {
                console.log(error);
            });
        } catch (error){
            console.error(error);
        }
    }

    request_lift(to_floor, from_floor)
    {
        try {
            fetch('http://localhost:8000/api/lift/request/', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                from_floor: from_floor,
                to_floor: to_floor,
            })
            }).then((res) => {
                return res.json();
            }).catch((error) => {
                console.log(error);
            }).then((data) => {
                if(!this.state.elevator_choice.includes(data["lift"]))
                {
                    const elevator_choices = this.state.elevator_choice;
                    elevator_choices.push(data["lift"]);
                    this.setState({elevator_choice : elevator_choices});

                    const intervalId = setInterval(() => {
                        this.get_lift_status(intervalId); // Fetch data every 1 second not the best solution but allows for updates to lifts floor.
                    }, 1000);
                }
            }).catch((error) => {
                console.log(error);
            });
        } catch (error){
            console.error(error);
        }
    }

    // On mount load lift data for serviced floors
    componentDidMount() 
    {   try
        {
            fetch('http://127.0.0.1:8000/api/lift/config/')
            .then((res) => {
            return res.json();
            })
            .catch((error) => {
                console.log(error);
            })
            .then((data) => {
            let avaliable_floors = [];
            for (let lift of data["lifts"]){
                // Only show floors reachable from current floor
                if (lift["serviced_floors"].includes(this.props.current_floor)) {
                    avaliable_floors = avaliable_floors.concat(lift["serviced_floors"].filter(item2 =>
                        !avaliable_floors.some(item1 => item1 === item2)
                    ));
                }
            }
            this.setState({data : avaliable_floors});
            }).catch((error) => {
                console.log(error);
            });
        } catch (error){
            console.error(error);
        }
    }

    render()
    {
        return ( <div data-testid="LiftConsole">
            <Card style={{ width: '100%' }}>
                <Card.Body>
                    <Card.Title>Lift Console</Card.Title>
                    <Card.Text>Go to lift: {this.state.elevator_choice.toString()}</Card.Text>
                        {this.state.data.map((floor_number) => ( <Button data-testid="LiftConsoleButton" variant="primary" onClick={() => this.request_lift(floor_number, this.props.current_floor)}>{floor_number}</Button>))}
                </Card.Body>
            </Card>
        </div>
        );
    }
}
export default LiftConsole;
