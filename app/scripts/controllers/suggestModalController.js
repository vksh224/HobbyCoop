'use strict';

/**
* This method closes the modal
*/
angular.module('h4hApp').controller(
  'SuggestModalController', function($scope, $http, close, item_request_id) {
  $scope.close = function(result) {
    console.log(result);
    close(result, 500); // close, but give 500ms for bootstrap to animate
  };
 
  $scope.suggestExchangeTimeAndLocation = function(){
    $scope.fromTime=$('#returnRequestFromDateTimepicker1 input').val();
    $scope.toTime=$('#returnRequestToDateTimepicker1 input').val();
    $scope.meetupAt = $('#Autocomplete').val();
    console.log("Here in suggest modal " + $scope.fromTime+" "+$scope.toTime+" "+ $scope.meetupAt+" "+ item_request_id);
    var dataObj = {
      fromTime : $scope.fromTime,
      toTime : $scope.toTime,
      meetupAt : $scope.meetupAt,
      item_request_id: item_request_id
    };	
    var res = $http.post(
      server_url + 'suggestExchangeTimeAndLocation',
      dataObj
    );
    res.success(function(data, status, headers, config) {
      $scope.message = data;
    });
    res.error(function(data, status, headers, config) {
      alert( "failure message: " + JSON.stringify({data: data}));
    });
  }

  $scope.suggestReturnTimeAndLocation = function(){
    $scope.fromTime=$('#returnRequestFromDateTimepicker1 input').val();
    $scope.toTime=$('#returnRequestToDateTimepicker1 input').val();
    $scope.meetupAt = $('#Autocomplete').val();
    console.log("Here in suggest return modal " + $scope.fromTime+" "+$scope.toTime+" "+ $scope.meetupAt+" "+ item_request_id);
    var dataObj = {
      fromTime : $scope.fromTime,
      toTime : $scope.toTime,
      meetupAt : $scope.meetupAt,
      tx_id: item_request_id
    };	
    var res = $http.post(
      server_url + 'suggestReturnTimeAndLocation',
      dataObj
    );
    res.success(function(data, status, headers, config) {
      $scope.message = data;
    });
    res.error(function(data, status, headers, config) {
      alert( "failure message: " + JSON.stringify({data: data}));
    });
  }

});

