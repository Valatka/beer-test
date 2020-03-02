import React from 'react';

import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import InputGroup from 'react-bootstrap/InputGroup';
import FormControl from 'react-bootstrap/FormControl';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Accordion from 'react-bootstrap/Accordion';
import Card from 'react-bootstrap/Card';
import ListGroup from 'react-bootstrap/ListGroup';

import './app.css'

class App extends React.Component {

    constructor() {
        super();

        this.state = {
            beer : [],
            breweries : ['Enter valid coordinates'],
            lat : React.createRef(),
            long: React.createRef(),
            numberOfRuns : React.createRef(),
            distance : []
        };
    }

    findPath() {
        fetch(`/api/find-path/${ this.state.lat.current.value }/${ this.state.long.current.value }/${ this.state.numberOfRuns.current.value }`)
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({
                        beer : result['beer'],
                        breweries : result['breweries'],
                        distance : result['distance']
                    })


                },

                (error) => {
                    this.setState({
                        beer : [],
                        breweries : ['Enter valid coordinates'],
                        distance : []

                    })
                    
                }
            );
    }

    render() {
        return (
            <Container fluid className="h-100">
                <div id="wrapper">
                    <Row>
                        <Col className="text-center">
                            <h1 id="title">Beer test</h1>
                        </Col>
                    </Row>
                    <Row className="py-5 justify-content-center">
                        <Col md={3} className="mb-3">
                            <InputGroup>
                                <FormControl
                                  placeholder="Latitude"
                                  className="mr-4"
                                  ref={ this.state.lat }
                                />
                            </InputGroup>
                        </Col>
                        <Col className="mb-3" md={3}>
                                
                                <InputGroup>
                                    <FormControl
                                      placeholder="Longitude"
                                      className="mr-4"

                                      ref={ this.state.long }
                                    />
                                </InputGroup>
                            
                        </Col>
                        <Col className="mb-3" md={3}>
                                
                                <InputGroup>
                                    <FormControl
                                      placeholder="number of runs"
                                      className="mr-4"

                                      ref={ this.state.numberOfRuns }
                                    />
                                </InputGroup>
                            
                        </Col>
                        <Col md={1} className="mb-3">
                            <Button variant="outline-light" onClick={ (e) => this.findPath(e) }>Find route</Button>
                        </Col>
                    </Row>
                    <Row>
                        <Accordion defaultActiveKey="0" className="w-75 mx-auto">
                            <Card>
                                <Card.Header className="d-flex justify-content-center">
                                    <Accordion.Toggle as={ Button } variant="light" eventKey="0" className="flex-grow-1">
                                        Visited breweries
                                    </Accordion.Toggle>
                                </Card.Header>
                                <Accordion.Collapse eventKey="0">
                                    <Card.Body>
                                        <ListGroup variant="flush">
                                            <ListGroup.Item>Visited { Math.max(0, this.state.breweries.length-2) } beer factories</ListGroup.Item>
                                            { this.state.breweries.map((value, i) => {
                                                if (value.id === undefined) {
                                                    return <ListGroup.Item key={i}>{ value }</ListGroup.Item>
                                                } else {
                                                    return <ListGroup.Item key={i}>{ `[${value.id}] ${value.name} ${value.lat} ${value.long} ${this.state.distance[i]} km` } </ListGroup.Item>
                                                }
                                                
                                            }) }
                                            <ListGroup.Item>Total distance traveled: { Math.round(this.state.distance.reduce((a, b) => a + b, 0), 3) } km </ListGroup.Item>
                                        </ListGroup>
                                    </Card.Body>
                                </Accordion.Collapse>
                            </Card>

                            <Card>
                                <Card.Header className="d-flex justify-content-center">
                                    <Accordion.Toggle as={ Button } variant="light" eventKey="1" className="flex-grow-1">
                                        Beer types collected
                                    </Accordion.Toggle>
                                </Card.Header>
                                <Accordion.Collapse eventKey="1">
                                    <Card.Body>
                                        <ListGroup variant="flush">
                                            <ListGroup.Item>Collected { this.state.beer.length } beer types</ListGroup.Item>
                                            { this.state.beer.map((value, i) => 
                                                <ListGroup.Item key={i}>{ value }</ListGroup.Item>
                                            ) }
                                        </ListGroup>
                                    </Card.Body>
                                </Accordion.Collapse>
                            </Card>
                        </Accordion>
                    </Row>
                </div>
            </Container>
        );
    }
    
}

export default App;
