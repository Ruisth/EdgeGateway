// Package main implementa o chaincode de rastreamento de datasets C2DTA.
//
// Ancora hashes de datasets IPFS no ecosystem ledger (Hyperledger Fabric),
// garantindo proveniencia e integridade dos dados do Digital Twin.
// Ver paper EdgeGateway_Paper.pdf (Seccao 3.2.6 — SD Twinning).
package main

import (
	"encoding/json"
	"fmt"
	"strconv"
	"time"

	"github.com/hyperledger/fabric-chaincode-go/v2/shim"
	pb "github.com/hyperledger/fabric-protos-go-apiv2/peer"
)

// Dataset representa um snapshot de dados do Digital Twin armazenado no IPFS.
type Dataset struct {
	DatasetID  string `json:"datasetID"`
	DeviceID   string `json:"deviceID"`
	IPFSHash   string `json:"ipfsHash"`
	OwnerDID   string `json:"ownerDID"`
	SizeBytes  int64  `json:"sizeBytes"`
	RecordCount int   `json:"recordCount"`
	StartTime  string `json:"startTime"`
	EndTime    string `json:"endTime"`
	CreatedAt  string `json:"createdAt"`
}

// DatasetTrackingChaincode implementa o contrato inteligente para rastreamento de datasets.
type DatasetTrackingChaincode struct{}

// Init e chamado durante a instanciacao do chaincode.
func (t *DatasetTrackingChaincode) Init(stub shim.ChaincodeStubInterface) *pb.Response {
	return shim.Success(nil)
}

// Invoke encaminha chamadas para as funcoes adequadas.
func (t *DatasetTrackingChaincode) Invoke(stub shim.ChaincodeStubInterface) *pb.Response {
	function, args := stub.GetFunctionAndParameters()

	switch function {
	case "RegisterDataset":
		return t.RegisterDataset(stub, args)
	case "QueryDataset":
		return t.QueryDataset(stub, args)
	case "QueryDatasetsByDevice":
		return t.QueryDatasetsByDevice(stub, args)
	case "TransferDatasetOwnership":
		return t.TransferDatasetOwnership(stub, args)
	default:
		return shim.Error(fmt.Sprintf("funcao desconhecida: %s", function))
	}
}

// RegisterDataset regista um novo dataset no ledger (UC6).
// Args: [datasetID, deviceID, ipfsHash, ownerDID, sizeBytes, recordCount, startTime, endTime]
func (t *DatasetTrackingChaincode) RegisterDataset(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 8 {
		return shim.Error("esperados 8 argumentos: datasetID, deviceID, ipfsHash, ownerDID, sizeBytes, recordCount, startTime, endTime")
	}

	sizeBytes, err := strconv.ParseInt(args[4], 10, 64)
	if err != nil {
		return shim.Error(fmt.Sprintf("sizeBytes invalido (%q): %v", args[4], err))
	}
	recordCount, err := strconv.Atoi(args[5])
	if err != nil {
		return shim.Error(fmt.Sprintf("recordCount invalido (%q): %v", args[5], err))
	}

	dataset := Dataset{
		DatasetID:   args[0],
		DeviceID:    args[1],
		IPFSHash:    args[2],
		OwnerDID:    args[3],
		SizeBytes:   sizeBytes,
		RecordCount: recordCount,
		StartTime:   args[6],
		EndTime:     args[7],
		CreatedAt:   time.Now().UTC().Format(time.RFC3339),
	}

	key, err := stub.CreateCompositeKey("Dataset", []string{dataset.DeviceID, dataset.DatasetID})
	if err != nil {
		return shim.Error(fmt.Sprintf("erro ao construir chave: %v", err))
	}
	data, err := json.Marshal(dataset)
	if err != nil {
		return shim.Error(fmt.Sprintf("erro ao serializar dataset: %v", err))
	}
	if err := stub.PutState(key, data); err != nil {
		return shim.Error(fmt.Sprintf("erro ao guardar dataset: %v", err))
	}
	if err := stub.SetEvent("DatasetRegistered", data); err != nil {
		return shim.Error(fmt.Sprintf("erro ao emitir evento: %v", err))
	}
	return shim.Success(data)
}

// QueryDataset retorna um dataset especifico.
// Args: [deviceID, datasetID]
func (t *DatasetTrackingChaincode) QueryDataset(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 2 {
		return shim.Error("esperados 2 argumentos: deviceID, datasetID")
	}

	key, err := stub.CreateCompositeKey("Dataset", []string{args[0], args[1]})
	if err != nil {
		return shim.Error(fmt.Sprintf("erro ao construir chave: %v", err))
	}
	data, err := stub.GetState(key)
	if err != nil {
		return shim.Error(fmt.Sprintf("erro ao ler dataset: %v", err))
	}
	if data == nil {
		return shim.Error(fmt.Sprintf("dataset nao encontrado: %s/%s", args[0], args[1]))
	}
	return shim.Success(data)
}

// QueryDatasetsByDevice lista todos os datasets de um dispositivo.
// Args: [deviceID]
func (t *DatasetTrackingChaincode) QueryDatasetsByDevice(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 1 {
		return shim.Error("esperado 1 argumento: deviceID")
	}

	iter, err := stub.GetStateByPartialCompositeKey("Dataset", []string{args[0]})
	if err != nil {
		return shim.Error(fmt.Sprintf("erro na query: %v", err))
	}
	defer iter.Close()

	var results []json.RawMessage
	for iter.HasNext() {
		kv, err := iter.Next()
		if err != nil {
			return shim.Error(fmt.Sprintf("erro na iteracao: %v", err))
		}
		results = append(results, kv.Value)
	}

	data, err := json.Marshal(results)
	if err != nil {
		return shim.Error(fmt.Sprintf("erro ao serializar resultados: %v", err))
	}
	return shim.Success(data)
}

// TransferDatasetOwnership transfere a propriedade de um dataset (UC8).
// Args: [deviceID, datasetID, newOwnerDID]
func (t *DatasetTrackingChaincode) TransferDatasetOwnership(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 3 {
		return shim.Error("esperados 3 argumentos: deviceID, datasetID, newOwnerDID")
	}

	key, err := stub.CreateCompositeKey("Dataset", []string{args[0], args[1]})
	if err != nil {
		return shim.Error(fmt.Sprintf("erro ao construir chave: %v", err))
	}
	data, err := stub.GetState(key)
	if err != nil {
		return shim.Error(fmt.Sprintf("erro ao ler dataset: %v", err))
	}
	if data == nil {
		return shim.Error(fmt.Sprintf("dataset nao encontrado: %s/%s", args[0], args[1]))
	}

	var dataset Dataset
	if err := json.Unmarshal(data, &dataset); err != nil {
		return shim.Error(fmt.Sprintf("estado corrompido para %s/%s: %v", args[0], args[1], err))
	}
	dataset.OwnerDID = args[2]

	updated, err := json.Marshal(dataset)
	if err != nil {
		return shim.Error(fmt.Sprintf("erro ao serializar dataset: %v", err))
	}
	if err := stub.PutState(key, updated); err != nil {
		return shim.Error(fmt.Sprintf("erro ao guardar dataset: %v", err))
	}
	if err := stub.SetEvent("DatasetOwnershipTransferred", updated); err != nil {
		return shim.Error(fmt.Sprintf("erro ao emitir evento: %v", err))
	}
	return shim.Success(updated)
}

func main() {
	if err := shim.Start(new(DatasetTrackingChaincode)); err != nil {
		fmt.Printf("erro ao iniciar chaincode: %v\n", err)
	}
}
