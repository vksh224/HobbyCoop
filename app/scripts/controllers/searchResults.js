'use strict';

angular.module('h4hApp').controller(
  'SearchResultsCtrl',
  ['$scope', '$http', 'ModalService', 'ItemService', 'UserService', 
    function($scope, $http, ModalService, ItemService,UserService) {
      $scope.itemsList = [];

      //hardcoded, once sign in works, it would handled
      $scope.user_id = UserService.getUserId();
      $scope.$watch(
        function () {return ItemService.getSearchResults()},
        function (newVal, oldVal) {
          $scope.searchResults = ItemService.getSearchResults();
        }
      );

      // $scope.$watch(function () { return ItemService.getCategories() }, function (newVal, oldVal) {
      //     $scope.categoryList = ItemService.getCategories();
      // });
      // $scope.$watch(function () { return ItemService.getItems() }, function (newVal, oldVal) {
      //     $scope.itemsList = ItemService.getItems();
      // });

      $scope.requestItem = function(itemId, dailyRate, userId) {
        console.log("Item : " + itemId);
        ModalService.showModal({
          templateUrl: 'modals/requestItemModal.html',
          controller: "RentRequestModalController",
          inputs:{
            item_id: itemId,
            daily_rate: dailyRate,
            rentee_id: userId
          }
        }).then(function(modal) {
          modal.element.modal();
          modal.close.then(function(result) {
            $scope.message = "You said " + result;
          });
        });
      };

      // Users can list an item they own when they see the search page.
      $scope.listItem = function(itemTypeId, userId) {
        console.log("User is listing a new item of type: " + itemTypeId);
        ModalService.showModal({
          templateUrl: 'modals/listItemModal.html',
          controller: "ListItemModalController",
          inputs:{
            item_type_id: itemTypeId,
            owner_id: userId
          }
        }).then(function(modal) {
          modal.element.modal();
          modal.close.then(function(result) {
            $scope.message = "Item listed! " + result;
          });
        });
      };

    }
  ]);
