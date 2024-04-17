import logo from './logo.svg';
import './App.css';
import LiftConsole from './lift_console.js';
import 'bootstrap/dist/css/bootstrap.min.css';

// Change this if you'd like to change the floor the interface is on.
const CURRENT_FLOOR = 0;

function App() {
  return (
    <div className="App" data-testid="App">
      <LiftConsole current_floor={CURRENT_FLOOR}/> 
    </div>
  );
}

export default App;
