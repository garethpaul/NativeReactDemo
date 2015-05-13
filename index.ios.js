/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 */
'use strict';

var React = require('react-native');
var {
  AppRegistry,
  StyleSheet,
  Image,
  Text,
  View,
} = React;

var MOCKED_MOVIES_DATA = [
  {title: 'Title', year: '2015', posters: {thumbnail: 'http://i.imgur.com/UePbdph.jpg'}},
];


var WowNativeReact = React.createClass({
  render: function() {
    return (
      <View style={styles.container}>
        <Text>Hi</Text>
        <Image
          style={styles.thumbnail}
          source={{uri: 'https://pbs.twimg.com/profile_images/562025976066867200/y5YY5Tb6_400x400.jpeg'}} />
      </View>
    );
  }
});

var styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5FCFF',
  },
  thumbnail: {
    width: 100,
    height: 100,
    borderRadius: 49,
  },
});

AppRegistry.registerComponent('WowNativeReact', () => WowNativeReact);
