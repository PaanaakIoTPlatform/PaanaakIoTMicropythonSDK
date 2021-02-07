import urequests as requests


class PaanaakDevice(object):
    """
    A class to provide request handlers to https://paanaak-cloud.ir API
    """
    def __init__(self, secret_key: str):
        """
        Args:
            secret_key(str): an id for each device that you create in the website would be accessible in the panel
        """
        self.constant_url = 'https://paanaak-cloud.ir/api/Device/DeviceCall?='
        self.secret_key = secret_key
        self.flags = {'too many request': False, 'requests limit': False}
        self.__valid_sensor_types = {'str': str(), 'float': float(), 'bool': bool()}
        self.sensors = dict()

    def __exec_http__(self,payload,https):        
        url = self.constant_url + self.secret_key
        if(not https):
            url = self.constant_url.replace('https', 'http')        
        response = requests.get(url=url+payload)
        if response.status_code != 500:

            text = response.text.replace('#', '')
            text = text.replace('@', '')

            if text == 'too many request':
                self.flags['too many request'] = True
                data = {'message': 'Too many requests has been made recently', 'status': response.status_code,'error':True}
                return data

            elif text == 'requests limit':
                self.flags['requests limit'] = True
                data = {'message': 'You have reached beyond the request limit', 'status': response.status_code,'error':True}
                return data

            elif text != '':
                self.flags['too many request'] = False
                self.flags['requests limit'] = False

                StringResponse = {'Relays': list(map(int, text)),'error':False}
                return StringResponse
        else:
            return {'Internal Server Error': response.status_code,'error':True}

    def state_validator(self, state: str):
        """

        Args:
            state(str): a string to validate

        Returns:
            True for valid inputs and False for invalid inputs
        """
        if not isinstance(state, str):
            return False
        state = state.strip()
        for i in state:
            if i != '0' and i != '1':
                return False
        return True

    def get_sensor_valid_types(self):
        return list(self.__valid_sensor_types.keys())

    def get_status(self, https=True):
        """

        Args:
            https(bool): to determine the usage of http or https protocol

        Returns:
            dict that contains given status from server or dict with error title as key and error code as value
        """
        if https:
            url = self.constant_url + self.secret_key
        else:
            url = self.constant_url.replace('https', 'http')

        payload = 'UniqueId='+self.secret_key
        return self.__exec_http__(payload,https)

    def add_sensor(self, name: str, data_type: str):
        """

        Args:
            name(str): a string to identify the sensor (duplication is not allowed)
            data_type(str): a valid datatype from this list : ['str', 'float', 'bool']

        Returns:
            True for a successful operation and raises value error for invalid inputs
        """
        if not isinstance(name, str):
            raise ValueError('Sensor\' name should be a string')
        elif name == 'state':
            raise ValueError('state is a reserved property name and can not be chosen as a sensor name')
        elif name in self.sensors:
            raise ValueError('Duplication is not allowed')

        if isinstance(data_type, str) and data_type in self.__valid_sensor_types:
            self.sensors[name] = (self.__valid_sensor_types[data_type], data_type)
            return True
        else:
            raise ValueError('Please choose from valid sensor types : [\'str\', \'float\', \'bool\'] ')

    def __create_sensors_payload(self, sensor_values: dict):
        payload =""       
        for key in sensor_values:
            if key in self.sensors:
                if isinstance(sensor_values[key], type(self.sensors.get(key)[0])):
                    if self.sensors.get(key)[1] == 'bool':
                        payload+="&"+key+"=1" if sensor_values.get(key)  else  "&"+key+"=0"
                    else:
                        payload += "&"+key+"="+str(sensor_values.get(key))
                else:
                    raise ValueError('value that you entered for {} does not match it\'s type'.format(key))
            else:
                raise NameError('you can not add a value for a sensor which is not in your sensor list '
                                '-> {}'.format(key))  
        return payload

    def send_sensors_values(self, sensor_values: dict, https=True):
        """

        Args:
            sensor_values(dict): contains sensor names as keys and their new values as dictionary values
            https(bool): to determine the usage of http or https protocol

        Returns:
            the request's status code for valid inputs and proper exceptions for invalid inputs
        """
        payload=self.__create_sensors_payload(sensor_values)
        return self.__exec_http__(payload,https)  

    def __create_relays_payload(self,state):
        payload = ""     
        if state is not None:
            if self.state_validator(state=state):
                payload+='&state'+str(state)
            else:
                raise ValueError('state should be a string made of 1 and 0')
        else:
            raise ValueError('You can not pass None as state')
        return payload

    def send_relays_state(self, state, https=True):
        """

        Args:
            state(str): a string made of 0 and 1 for relays state
            https(bool): to determine the usage of http or https protocol

        Returns:
            the request's status code for valid inputs and proper exceptions for invalid inputs
        """
        payload=self.__create_relays_payload(state)
        return self.__exec_http__(payload,https)
    
    def send_sensors_and_relays(self, sensor_values: dict,state, https=True):
        """

        Args:
            sensor_values(dict): contains sensor names as keys and their new values as dictionary values
            state(str): a string made of 0 and 1 for relays state
            https(bool): to determine the usage of http or https protocol

        Returns:
            the request's status code for valid inputs and proper exceptions for invalid inputs
        """
        payload=""
        payload=self.__create_sensors_payload(sensor_values)
        payloadRelays=self.__create_relays_payload(state)
        payload+=payloadRelays            
        return self.__exec_http__(payload,https)


    