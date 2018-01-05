'use strict';

/**
 * @ngdoc function
 * @name h4hApp.controller:MyAccountCtrl
 * @description
 * # MyAccountCtrl
 * Controller of the h4hApp profile/account page
 */
angular.module('h4hApp')
  .controller('MyAccountCtrl', ['$scope','$http','ModalService','UserService','ItemService', function($scope, $http, ModalService, UserService,ItemService) {
     $scope.lentObjectsList = {};
     $scope.owner = {
          "dropOffItems" : [],
          "idleItems" : [],
          "rentRequestItems" : [],
          "rentedItems" : [],
   }

     $scope.rentee = {
          "_1returnScheduledItems": [],
          "_2pendingPickup" :[],
          "_3proposedReturnTimeItems":[],
          "_4pendingApproval" : [],
          "_5returnRequestedItems": [],
          "_6rentedActiveItems": [],
          "_7rentRequests": [],
          "_8completedTransactions" : [],
     }

     //console.log("Heelloo "  + $scope.rentee.completedTransactions);

     $scope.user_id = UserService.getUserId();
     console.log("The user is : " + $scope.user_id);
   	 //$scope.lentItemsList.foodtitle = '';

    $http({
      method: 'GET',
      url: server_url + 'user/'+$scope.user_id+'/items'
    })
    .success(function (data) {
      $scope.owner = {}; //data;
      $scope.owner.dropOffItems = data.itemDropOffs;
      $scope.owner.idleItems = data.idleItems;
      $scope.owner.rentRequestItems = data.rentRequests;
      $scope.owner.rentedItems = data.rentedItems;
    })
    .error(function (data) {
      console.log("Something went wrong when loading owner-specific items");
    // something went wrong :(
    });
  
    $scope.borrowedObjectsList = [];
   	 //$scope.lentItemsList.foodtitle = '';

    $http({
      method: 'GET',
      url: server_url + 'user/'+$scope.user_id+'/rentee'
    })
    .success(function (data, status, headers, config) {
      $scope.rentee = {};
      //console.log($scope.rentee);
      //console.log($scope.rentee.completedTransactions);
      $scope.rentee._1returnScheduledItems = data.returnScheduledItems;
      $scope.rentee._2pendingPickup = data.pendingPickup;
      $scope.rentee._3proposedReturnTimeItems = data.proposedReturnTimeItems;
      $scope.rentee._4pendingApproval = data.pendingApproval;
      $scope.rentee._5returnRequestedItems = data.returnRequestedItems;
      $scope.rentee._6rentedActiveItems = data.rentedActiveItems;
      $scope.rentee._7rentRequests = data.rentRequests;
      $scope.rentee._8completedTransactions = data.completedTransactions;
    })
    .error(function (data, status, headers, config) {
      console.log("Something went wrong with loading rentee data");
    // something went wrong :(
    });

    $scope.suggestExchangeTimeAndLocation = function(id) {
        ModalService.showModal({
            templateUrl: 'modals/suggestExchangeTimeAndLocation.html',
            controller: "SuggestModalController",
            inputs:{item_request_id: id}
        }).then(function(modal) {
            modal.element.modal();
            modal.close.then(function(result) {
                $scope.message = "You said " + result;
            });
        });
    };

    $scope.confirmExchangeTimeAndLocation = function(id) {
        ModalService.showModal({
            templateUrl: 'modals/confirmExchangeTimeAndLocation.html',
            controller: "ConfirmModalController",
            inputs:{item_request_id: id,
                    user_id: $scope.user_id}
        }).then(function(modal) {
            modal.element.modal();
            modal.close.then(function(result) {
                $scope.message = "You said " + result;
            });
        });
    };

    $scope.showReturnRequest = function(id) {
      console.log("You pressed the Suggest Return button!");
      ModalService.showModal({
        templateUrl: 'modals/suggestReturnTimeAndLocation.html',
        controller: "SuggestModalController",
        inputs:{item_request_id: id,
                user_id: $scope.user_id}
      }).then(function(modal) {
        modal.element.modal();
        modal.close.then(function(result) {
          $scope.message = "You said " + result;
        });
      });
    };


     $scope.scheduleReturnTimeAndLocation = function(id) {
        ModalService.showModal({
            templateUrl: 'modals/scheduleReturnTimeAndLocation.html',
            controller: "ScheduleReturnModalController",
            inputs:{item_request_id: id,
                    user_id: $scope.user_id}
        }).then(function(modal) {
            modal.element.modal();
            modal.close.then(function(result) {
                $scope.message = "You said " + result;
            });
        });
    };

    $scope.requestItemReturn = function(itemId){
        ItemService.requestReturnItem($scope.user_id, itemId);
    }
    $scope.confirmItemPickup = function(itemId){
        ItemService.confirmItemPickup($scope.user_id, itemId);
    }
    $scope.confirmItemReturn = function(returnTimeId){
        ItemService.confirmItemReturn($scope.user_id, returnTimeId);
    }
    $scope.deleteItem = function(itemId){
        ItemService.deleteItem($scope.user_id, itemId);
    }

}]);
