'use strict';

/**
 * @ngdoc function
 * @name h4hApp.controller:RentAnItemCtrl
 * @description
 * # RentAnItemCtrl
 * Controller of the h4hApp
 */
angular.module('h4hApp').controller('RentAnItemCtrl', ['$scope','fileUpload' ,function($scope, fileUpload) {
    $scope.submit = function(valid) {
      if(valid) {
        // TODO: post to server
      }
    };

     $scope.uploadFile = function(){
        var file = $scope.myFile;
        console.log('file is ' );
        console.dir(file);
        var uploadUrl = "/fileUpload";
        fileUpload.uploadFileToUrl(file, uploadUrl);
    };

  }]);
