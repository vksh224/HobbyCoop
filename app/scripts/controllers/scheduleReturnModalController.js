'use strict';

/**
* This method closes the modal
*/
angular.module('h4hApp').controller(
  'ScheduleReturnModalController',
  function($scope, $http, close, item_request_id, user_id) {
  $scope.close = function(result) {
    console.log("You made it to the ScheduleReturnModalController!");
    console.log(result);
    close(result, 500); // close, but give 500ms for bootstrap to animate
  };
  $scope.scheduleReturnTimeAndLocation = function(){
    $scope.exactTime=$('#pickDateTimePicker1 input').val();
    $scope.meetupAt = $('#meetupAt').html();
    
    console.log("Here in confirm modal " + $scope.exactTime+" "+$scope.meetupAt+" "+ item_request_id);
    var dataObj = {
      exactTime: $scope.exactTime,
      meetupAt: $scope.meetupAt,
      return_request_id: item_request_id,
      user_id: user_id,
    };	
    var res = $http.post(server_url + 'scheduleReturn', dataObj);
    res.success(function(data, status, headers, config) {
      $scope.message = data;
    });
    res.error(function(data, status, headers, config) {
      alert( "failure message: " + JSON.stringify({data: data}));
    });
  }
});

