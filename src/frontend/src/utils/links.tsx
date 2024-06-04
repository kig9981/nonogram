import React from 'react';

const api_server_protocol = process.env.REACT_APP_API_SERVER_PROTOCOL;
const api_server_host = process.env.REACT_APP_API_SERVER_HOST;
const api_server_port = process.env.REACT_APP_API_SERVER_PORT;

export const api_server_url = api_server_protocol + '://' + 'localhost' + ':' + api_server_port;