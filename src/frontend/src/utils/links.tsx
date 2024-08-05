import { env } from '../env'

const api_server_protocol = env.REACT_APP_API_SERVER_PROTOCOL;
const api_server_domain = env.REACT_APP_API_SERVER_DOMAIN;

export const api_server_url = `${api_server_protocol}://${api_server_domain}/api`;