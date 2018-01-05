'use strict';

/**
* This method closes the modal
*/
angular.module('h4hApp').controller('SignInModalController', function($scope, $http, UserService, close) {
  $scope.close = function(result) {
    console.log(result);
    console.log($scope.emailId+"   "+ $scope.password);
    UserService.setUserId($scope.emailId, $scope.password);
    
    close(result, 500); // close, but give 500ms for bootstrap to animate
  };
 //  $scope.fromTime=$('#returnRequestFromDateTimepicker1 input').val();
 // $scope.$watch(function () { return $('#returnRequestFromDateTimepicker1 input').val() }, function (newVal, oldVal) {
 //         $scope.fromTime=$('#returnRequestFromDateTimepicker1 input').val();
 //         console.log($scope.fromTime);
 //    });
});

