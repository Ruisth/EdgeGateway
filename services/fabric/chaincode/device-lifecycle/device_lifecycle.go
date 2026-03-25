// Package main implementa o chaincode de ciclo de vida de dispositivos C2DTA.
//
// Gere os 6 estados definidos no paper EdgeGateway_Paper.pdf (Seccao 3.1):
//
//	Manufactured → Available → In-Transit → Claimed → Twinned → Decommissioned
package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-chaincode-go/v2/shim"
	pb "github.com/hyperledger/fabric-protos-go-apiv2/peer"
)

// ---------- Constantes de estado ----------

const (
	StateManufactured    = "Manufactured"
	StateAvailable       = "Available"
	StateInTransit       = "In-Transit"
	StateClaimed         = "Claimed"
	StateTwinned         = "Twinned"
	StateDecommissioned  = "Decommissioned"
)

// ---------- Modelos ----------

// DeviceModel representa um modelo de dispositivo registado no ecossistema.
type DeviceModel struct {
	ModelID      string `json:"modelID"`
	Manufacturer string `json:"manufacturer"`
	WoTTDHash    string `json:"wotTDHash"`
	CreatedAt    string `json:"createdAt"`
}

// Device representa um dispositivo no ecossistema C2DTA.
type Device struct {
	DeviceID        string `json:"deviceID"`
	ModelID         string `json:"modelID"`
	State           string `json:"state"`
	ManufacturerID  string `json:"manufacturerID"`
	OwnerDID        string `json:"ownerDID"`
	ControllerDID   string `json:"controllerDID"`
	GenesisVCHash   string `json:"genesisVCHash"`
	OwnershipVCHash string `json:"ownershipVCHash"`
	DittoThingID    string `json:"dittoThingID"`
	CreatedAt       string `json:"createdAt"`
	UpdatedAt       string `json:"updatedAt"`
}

// ---------- Chaincode ----------

// DeviceLifecycleChaincode implementa o contrato inteligente para gestao
// do ciclo de vida de dispositivos.
type DeviceLifecycleChaincode struct{}

// Init e chamado durante a instanciacao do chaincode.
func (t *DeviceLifecycleChaincode) Init(stub shim.ChaincodeStubInterface) *pb.Response {
	return shim.Success(nil)
}

// Invoke encaminha chamadas para as funcoes adequadas.
func (t *DeviceLifecycleChaincode) Invoke(stub shim.ChaincodeStubInterface) *pb.Response {
	function, args := stub.GetFunctionAndParameters()

	switch function {
	case "RegisterDeviceModel":
		return t.RegisterDeviceModel(stub, args)
	case "ManufactureDevice":
		return t.ManufactureDevice(stub, args)
	case "MakeAvailable":
		return t.MakeAvailable(stub, args)
	case "InitiateTransit":
		return t.InitiateTransit(stub, args)
	case "ClaimDevice":
		return t.ClaimDevice(stub, args)
	case "TwinDevice":
		return t.TwinDevice(stub, args)
	case "UntwinDevice":
		return t.UntwinDevice(stub, args)
	case "DecommissionDevice":
		return t.DecommissionDevice(stub, args)
	case "QueryDevice":
		return t.QueryDevice(stub, args)
	case "QueryDevicesByState":
		return t.QueryDevicesByState(stub, args)
	case "QueryDevicesByOwner":
		return t.QueryDevicesByOwner(stub, args)
	default:
		return shim.Error(fmt.Sprintf("funcao desconhecida: %s", function))
	}
}

// RegisterDeviceModel regista um modelo de dispositivo (UC2).
// Args: [modelID, manufacturer, wotTDHash]
func (t *DeviceLifecycleChaincode) RegisterDeviceModel(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 3 {
		return shim.Error("esperados 3 argumentos: modelID, manufacturer, wotTDHash")
	}

	model := DeviceModel{
		ModelID:      args[0],
		Manufacturer: args[1],
		WoTTDHash:    args[2],
		CreatedAt:    time.Now().UTC().Format(time.RFC3339),
	}

	key, _ := stub.CreateCompositeKey("DeviceModel", []string{model.ModelID})
	data, _ := json.Marshal(model)
	if err := stub.PutState(key, data); err != nil {
		return shim.Error(fmt.Sprintf("erro ao guardar modelo: %v", err))
	}

	stub.SetEvent("ModelRegistered", data)
	return shim.Success(data)
}

// ManufactureDevice regista um dispositivo fabricado (UC3).
// Args: [deviceID, modelID, manufacturerID, genesisVCHash]
func (t *DeviceLifecycleChaincode) ManufactureDevice(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 4 {
		return shim.Error("esperados 4 argumentos: deviceID, modelID, manufacturerID, genesisVCHash")
	}

	now := time.Now().UTC().Format(time.RFC3339)
	device := Device{
		DeviceID:       args[0],
		ModelID:        args[1],
		State:          StateManufactured,
		ManufacturerID: args[2],
		GenesisVCHash:  args[3],
		CreatedAt:      now,
		UpdatedAt:      now,
	}

	data, _ := json.Marshal(device)
	if err := stub.PutState(device.DeviceID, data); err != nil {
		return shim.Error(fmt.Sprintf("erro ao guardar dispositivo: %v", err))
	}

	stub.SetEvent("DeviceManufactured", data)
	return shim.Success(data)
}

// MakeAvailable transiciona Manufactured → Available.
// Args: [deviceID]
func (t *DeviceLifecycleChaincode) MakeAvailable(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 1 {
		return shim.Error("esperado 1 argumento: deviceID")
	}
	return t.transition(stub, args[0], StateManufactured, StateAvailable, func(d *Device) {})
}

// InitiateTransit transiciona Available → In-Transit (UC4).
// Args: [deviceID, buyerDID]
func (t *DeviceLifecycleChaincode) InitiateTransit(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 2 {
		return shim.Error("esperados 2 argumentos: deviceID, buyerDID")
	}
	return t.transition(stub, args[0], StateAvailable, StateInTransit, func(d *Device) {
		d.OwnerDID = args[1]
	})
}

// ClaimDevice transiciona In-Transit → Claimed (UC5).
// Args: [deviceID, controllerDID, ownershipVCHash]
func (t *DeviceLifecycleChaincode) ClaimDevice(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 3 {
		return shim.Error("esperados 3 argumentos: deviceID, controllerDID, ownershipVCHash")
	}
	return t.transition(stub, args[0], StateInTransit, StateClaimed, func(d *Device) {
		d.ControllerDID = args[1]
		d.OwnershipVCHash = args[2]
	})
}

// TwinDevice transiciona Claimed → Twinned (UC6).
// Args: [deviceID, dittoThingID]
func (t *DeviceLifecycleChaincode) TwinDevice(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 2 {
		return shim.Error("esperados 2 argumentos: deviceID, dittoThingID")
	}
	return t.transition(stub, args[0], StateClaimed, StateTwinned, func(d *Device) {
		d.DittoThingID = args[1]
	})
}

// UntwinDevice transiciona Twinned → Claimed (UC7).
// Args: [deviceID]
func (t *DeviceLifecycleChaincode) UntwinDevice(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 1 {
		return shim.Error("esperado 1 argumento: deviceID")
	}
	return t.transition(stub, args[0], StateTwinned, StateClaimed, func(d *Device) {
		d.DittoThingID = ""
	})
}

// DecommissionDevice transiciona qualquer estado → Decommissioned.
// Args: [deviceID]
func (t *DeviceLifecycleChaincode) DecommissionDevice(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 1 {
		return shim.Error("esperado 1 argumento: deviceID")
	}

	device, err := t.getDevice(stub, args[0])
	if err != nil {
		return shim.Error(err.Error())
	}

	device.State = StateDecommissioned
	device.UpdatedAt = time.Now().UTC().Format(time.RFC3339)

	data, _ := json.Marshal(device)
	stub.PutState(device.DeviceID, data)
	stub.SetEvent("DeviceDecommissioned", data)
	return shim.Success(data)
}

// QueryDevice retorna o estado atual de um dispositivo.
// Args: [deviceID]
func (t *DeviceLifecycleChaincode) QueryDevice(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 1 {
		return shim.Error("esperado 1 argumento: deviceID")
	}

	data, err := stub.GetState(args[0])
	if err != nil {
		return shim.Error(fmt.Sprintf("erro ao ler dispositivo: %v", err))
	}
	if data == nil {
		return shim.Error(fmt.Sprintf("dispositivo nao encontrado: %s", args[0]))
	}
	return shim.Success(data)
}

// QueryDevicesByState pesquisa dispositivos por estado (CouchDB rich query).
// Args: [state]
func (t *DeviceLifecycleChaincode) QueryDevicesByState(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 1 {
		return shim.Error("esperado 1 argumento: state")
	}

	query := fmt.Sprintf(`{"selector":{"state":"%s"}}`, args[0])
	return t.richQuery(stub, query)
}

// QueryDevicesByOwner pesquisa dispositivos por proprietario (CouchDB rich query).
// Args: [ownerDID]
func (t *DeviceLifecycleChaincode) QueryDevicesByOwner(stub shim.ChaincodeStubInterface, args []string) *pb.Response {
	if len(args) != 1 {
		return shim.Error("esperado 1 argumento: ownerDID")
	}

	query := fmt.Sprintf(`{"selector":{"ownerDID":"%s"}}`, args[0])
	return t.richQuery(stub, query)
}

// ---------- Funcoes auxiliares ----------

func (t *DeviceLifecycleChaincode) getDevice(stub shim.ChaincodeStubInterface, deviceID string) (*Device, error) {
	data, err := stub.GetState(deviceID)
	if err != nil {
		return nil, fmt.Errorf("erro ao ler dispositivo: %v", err)
	}
	if data == nil {
		return nil, fmt.Errorf("dispositivo nao encontrado: %s", deviceID)
	}

	var device Device
	if err := json.Unmarshal(data, &device); err != nil {
		return nil, fmt.Errorf("erro ao desserializar dispositivo: %v", err)
	}
	return &device, nil
}

func (t *DeviceLifecycleChaincode) transition(
	stub shim.ChaincodeStubInterface,
	deviceID, fromState, toState string,
	modify func(*Device),
) *pb.Response {
	device, err := t.getDevice(stub, deviceID)
	if err != nil {
		return shim.Error(err.Error())
	}

	if device.State != fromState {
		return shim.Error(fmt.Sprintf(
			"transicao invalida: dispositivo %s esta em '%s', esperado '%s'",
			deviceID, device.State, fromState,
		))
	}

	modify(device)
	device.State = toState
	device.UpdatedAt = time.Now().UTC().Format(time.RFC3339)

	data, _ := json.Marshal(device)
	if err := stub.PutState(deviceID, data); err != nil {
		return shim.Error(fmt.Sprintf("erro ao guardar dispositivo: %v", err))
	}

	eventName := fmt.Sprintf("Device%s", toState)
	stub.SetEvent(eventName, data)
	return shim.Success(data)
}

func (t *DeviceLifecycleChaincode) richQuery(stub shim.ChaincodeStubInterface, query string) *pb.Response {
	iter, err := stub.GetQueryResult(query)
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

	data, _ := json.Marshal(results)
	return shim.Success(data)
}

func main() {
	if err := shim.Start(new(DeviceLifecycleChaincode)); err != nil {
		fmt.Printf("erro ao iniciar chaincode: %v\n", err)
	}
}
