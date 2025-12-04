/**
 * Equipment Service - Business logic for equipment management.
 *
 * CRITICAL:
 * - Uses inject() NOT constructor injection
 * - Uses ApiConfigService for all endpoints (NO hardcoded URLs!)
 * - Returns RxJS Observables (lazy evaluation)
 */

import {inject, Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";
import {Observable} from "rxjs";
import {ApiConfigService} from "../config/api-config.service";
import {
    EquipmentCreateRequest,
    EquipmentDetailResponse,
    EquipmentListResponse,
    EquipmentStatus,
    EquipmentType,
    EquipmentUpdateRequest
} from "../../models/equipment.model";

@Injectable({
    providedIn: "root"
})
export class EquipmentService {
    private http = inject(HttpClient);
    private apiConfig = inject(ApiConfigService);

    /**
     * Create new equipment.
     *
     * @param data Equipment data (plaintext password, license_key, price will be encrypted by backend)
     * @returns Observable of EquipmentDetailResponse
     *
     * @example
     * this.equipmentService.createEquipment({
     *   type: EquipmentType.SOFTWARE,
     *   name: 'Logic Pro X',
     *   manufacturer: 'Apple',
     *   password: 'my-secret',
     *   price: '299.99 EUR'
     * }).subscribe({
     *   next: (response) => console.log('Created:', response.data.id),
     *   error: (error) => console.error('Failed:', error)
     * });
     */
    createEquipment(data: EquipmentCreateRequest): Observable<EquipmentDetailResponse> {
        return this.http.post<EquipmentDetailResponse>(
            this.apiConfig.endpoints.equipment.create(),
            data
        );
    }

    /**
     * Get paginated equipment list with filters.
     *
     * @param limit Items per page (default 20)
     * @param offset Pagination offset (default 0)
     * @param type Filter by type (optional)
     * @param status Filter by status (optional)
     * @param search Search term for name/manufacturer/tags (optional)
     * @returns Observable of EquipmentListResponse
     *
     * @example
     * this.equipmentService.getEquipments(20, 0, EquipmentType.SOFTWARE, EquipmentStatus.ACTIVE, 'Logic')
     *   .subscribe(response => {
     *     console.log('Total:', response.pagination.total);
     *     console.log('Items:', response.data);
     *   });
     */
    getEquipments(
        limit: number = 20,
        offset: number = 0,
        type?: EquipmentType,
        status?: EquipmentStatus,
        search?: string
    ): Observable<EquipmentListResponse> {
        return this.http.get<EquipmentListResponse>(
            this.apiConfig.endpoints.equipment.list(limit, offset, type, status, search)
        );
    }

    /**
     * Get equipment by ID (with decrypted sensitive fields).
     *
     * @param id Equipment UUID
     * @returns Observable of EquipmentDetailResponse (password, license_key, price decrypted)
     *
     * @example
     * this.equipmentService.getEquipmentById('123e4567-e89b-12d3-a456-426614174000')
     *   .subscribe(response => {
     *     console.log('Equipment:', response.data);
     *     console.log('Password:', response.data.password); // Decrypted
     *   });
     */
    getEquipmentById(id: string): Observable<EquipmentDetailResponse> {
        return this.http.get<EquipmentDetailResponse>(
            this.apiConfig.endpoints.equipment.detail(id)
        );
    }

    /**
     * Update equipment (partial update).
     *
     * @param id Equipment UUID
     * @param data Fields to update (plaintext password, license_key, price will be encrypted by backend)
     * @returns Observable of EquipmentDetailResponse
     *
     * @example
     * this.equipmentService.updateEquipment(id, {
     *   status: EquipmentStatus.ARCHIVED,
     *   price: '349.99 EUR'
     * }).subscribe({
     *   next: () => console.log('Updated'),
     *   error: (error) => console.error('Failed:', error)
     * });
     */
    updateEquipment(id: string, data: EquipmentUpdateRequest): Observable<EquipmentDetailResponse> {
        return this.http.put<EquipmentDetailResponse>(
            this.apiConfig.endpoints.equipment.update(id),
            data
        );
    }

    /**
     * Delete equipment.
     *
     * @param id Equipment UUID
     * @returns Observable of { message: string }
     *
     * @example
     * this.equipmentService.deleteEquipment(id).subscribe({
     *   next: (response) => console.log(response.message),
     *   error: (error) => console.error('Failed:', error)
     * });
     */
    deleteEquipment(id: string): Observable<{ message: string }> {
        return this.http.delete<{ message: string }>(
            this.apiConfig.endpoints.equipment.delete(id)
        );
    }
}
