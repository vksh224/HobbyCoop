'use strict';

/**
* This method closes the modal
*/
angular.module('h4hApp').controller('RentRequestModalController', function($scope, $http, close, item_id, daily_rate, rentee_id) {
  $scope.duration = 0;
  $scope.cost = 0;
  //console.log($scope.duration+"   "+$scope.cost);
  $scope.close = function(result) {  
    close(result, 500); // close, but give 500ms for bootstrap to animate
  };

  $scope.calculateCost = function(){
    $scope.cost = "$" + $scope.duration * daily_rate;
  }

  $scope.requestItem = function(){
    $scope.fromTime=$('#rentRequestFromDateTimepicker1 input').val();
    //$scope.toTime=$('#rentRequestToDateTimepicker1 input').val();

    //$scope.meetupAt = $('#Autocomplete').val();
    console.log("Here in request Item modal, fromtime: " + $scope.fromTime+", itemDuration: "
    	+$scope.duration+", dailyRate: $"+daily_rate + ", totalCost: "+$scope.cost+", itemID: "+ item_id+ ", renteeID: "+rentee_id);
    var dataObj = {
      start_time : $scope.fromTime,
      duration : $scope.duration,
      item_id: item_id,
      rentee_id : rentee_id
    };
    console.log(dataObj);	
    var res = $http.post(server_url + 'requestItem', dataObj);
    res.success(function(data, status, headers, config) {
      $scope.message = data;
    });
    res.error(function(data, status, headers, config) {
      alert( "failure message: " + JSON.stringify({data: data}));
    });
  }
});

